import logging
import os
from http import HTTPStatus
from typing import Union

from boto3 import client as boto3_client
from starlette.responses import JSONResponse

from constants.common_constants import CommonConstants, UserRoles
from model.admins.admin import AdminIn, AdminPatch
from model.user import (
    AuthResponse,
    Challenge,
    ChangePasswordRequest,
    ConfirmForgotPasswordRequest,
    ConfirmSignUp,
    Login,
    RefreshTokenRequest,
    SignUp,
    SignUpResponse,
    UpdateTemporaryPasswordRequest,
)
from usecase.admin_usecase import AdminUseCase
from usecase.email_usecase import EmailUsecase
from utils.utils import Utils


class AuthUsecase:
    def __init__(self) -> None:
        self.client = boto3_client('cognito-idp', region_name=os.environ['REGION'])
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.user_pool_client_id = os.getenv('USER_POOL_CLIENT_ID')
        self.client_secret = Utils.get_secret(os.getenv('CLIENT_SECRET_NAME'))
        self.email_uc = EmailUsecase()
        self.admin_uc = AdminUseCase()

    def signup(self, sign_up_details: SignUp):
        """
        Signs up a user in the cognito user pool.

        :param sign_up_details: The details of the user to sign up.
        :type sign_up_details: SignUp

        :raises Exception: Bad request message if an error occurs.

        :return: The response to the sign-up request.
        :rtype: SignUpResponse or JSONResponse
        """
        try:
            auth_response = self.client.sign_up(
                ClientId=self.user_pool_client_id,
                Username=sign_up_details.email,
                Password=sign_up_details.password,
                SecretHash=Utils.compute_secret_hash(
                    client_secret=self.client_secret,
                    user_name=sign_up_details.email,
                    client_id=self.user_pool_client_id,
                ),
            )
            sub = auth_response['UserSub']
            res = SignUpResponse(
                email=sign_up_details.email,
                sub=sub,
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return res

    def confirm_signup(self, confirm_signup: ConfirmSignUp):
        """
        Validates user sign up through a confirmation code.

        :param confirm_signup: The details of the user to confirm sign up.
        :type confirm_signup: ConfirmSignUp

        :raises Exception: Bad request message if an error occurs.

        :return: The response to the confirm sign up request.
        :rtype: JSONResponse
        """
        try:
            self.client.confirm_sign_up(
                SecretHash=Utils.compute_secret_hash(
                    client_secret=self.client_secret,
                    user_name=confirm_signup.email,
                    client_id=self.user_pool_client_id,
                ),
                Username=confirm_signup.email,
                ClientId=self.user_pool_client_id,
                ConfirmationCode=confirm_signup.confirmationCode,
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    'message': 'User confirmed successfully',
                },
            )

    def login(self, login_details: Login):
        """
        Logs in user in the cognito user pool.

        :param login_details: The details of the user to log in.
        :type login_details: Login

        :raises Exception: Bad request message if an error occurs.

        :return: The response to the login request.
        :rtype: AuthResponse or Challenge
        """
        try:
            response = self.client.initiate_auth(
                ClientId=self.user_pool_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': login_details.email,
                    'PASSWORD': login_details.password,
                    'SECRET_HASH': Utils.compute_secret_hash(
                        client_secret=self.client_secret,
                        user_name=login_details.email,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )

            auth_result = response.get('AuthenticationResult')
            session = response.get('Session')
            if auth_result is None:
                challenge_name = response.get('ChallengeName')
                if challenge_name == 'NEW_PASSWORD_REQUIRED':
                    return Challenge(
                        challengeName=challenge_name,
                        session=session,
                    )
                else:
                    return JSONResponse(
                        status_code=HTTPStatus.BAD_REQUEST,
                        content={
                            'message': 'Invalid credentials',
                        },
                    )

            access_token = auth_result.get('AccessToken')
            user_info = self.client.get_user(AccessToken=access_token)
            auth_model = AuthResponse(
                accessToken=access_token,
                expiresIn=auth_result.get('ExpiresIn'),
                tokenType=auth_result.get('TokenType'),
                refreshToken=auth_result.get('RefreshToken'),
                idToken=auth_result.get('IdToken'),
                session=session,
                sub=user_info.get('Username'),
            )

            auth_model_dict = auth_model.dict(exclude_none=True, exclude_unset=True)
            auth_response = JSONResponse(status_code=HTTPStatus.OK, content=auth_model_dict)
            auth_response.set_cookie(
                'Authorization',
                value=f'Bearer {auth_model.accessToken}',
                samesite='none',
                domain=CommonConstants.DOMAIN_NAME,
                secure=True,
                httponly=True,
            )
            auth_response.set_cookie(
                'Refresh-Token',
                value=auth_model.refreshToken,
                samesite='none',
                domain=CommonConstants.DOMAIN_NAME,
                secure=True,
                httponly=True,
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return auth_response

    def refresh(self, refresh_token_request: RefreshTokenRequest):
        """
        Obtains new tokens.

        :param refresh_token_request: The details of the refresh token request.
        :type refresh_token_request: RefreshTokenRequest

        :raises Exception: Bad request message if an error occurs.

        :return: The response to the refresh token request.
        :rtype: JSONResponse
        """
        try:
            username = refresh_token_request.sub
            response = self.client.initiate_auth(
                ClientId=self.user_pool_client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token_request.refreshToken,
                    'SECRET_HASH': Utils.compute_secret_hash(
                        client_secret=self.client_secret,
                        user_name=username,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )

            auth_result = response.get('AuthenticationResult')

            auth_model = AuthResponse(
                accessToken=auth_result.get('AccessToken'),
                expiresIn=auth_result.get('ExpiresIn'),
                tokenType=auth_result.get('TokenType'),
                refreshToken=auth_result.get('RefreshToken'),
                idToken=auth_result.get('IdToken'),
                sub=username,
            )
            auth_model_dict = auth_model.dict(exclude_none=True, exclude_unset=True)
            auth_response = JSONResponse(status_code=HTTPStatus.OK, content=auth_model_dict)
            auth_response.set_cookie(
                'Authorization',
                value=f'Bearer {auth_model.accessToken}',
                samesite='none',
                domain=CommonConstants.DOMAIN_NAME,
                secure=True,
                httponly=True,
            )
            auth_response.set_cookie(
                'Refresh-Token',
                value=auth_model.refreshToken,
                samesite='none',
                domain=CommonConstants.DOMAIN_NAME,
                secure=True,
                httponly=True,
            )
            auth_response.set_cookie(
                'Username',
                value=username,
                samesite='none',
                domain=CommonConstants.DOMAIN_NAME,
                secure=True,
                httponly=True,
            )
            return auth_response
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})

    def sign_out(self, accessToken: str):
        """
        Signs out a user from the cognito user pool.

        :param accessToken: The access token of the user to sign out.
        :type accessToken: str

        :raises Exception: Bad request message if an error occurs.

        :return: The response to the sign-out request (i.e if operation was successful).
        :rtype: JSONResponse
        """
        try:
            self.client.global_sign_out(AccessToken=accessToken)
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    'message': 'User logged out successfully',
                },
            )

    def forgot_password(self, email: str):
        """
        Facilitates the initiation of a password reset process for a user.

        :param email: The email of the user requesting a password reset.
        :type email: str

        :raises Exception: Bad request message if an error occurs during the password reset process.

        :return: The response to the password reset request.
        :rtype: JSONResponse
        """
        try:
            self.client.forgot_password(
                ClientId=self.user_pool_client_id,
                Username=email,
                SecretHash=Utils.compute_secret_hash(
                    client_secret=self.client_secret,
                    user_name=email,
                    client_id=self.user_pool_client_id,
                ),
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    'message': 'Password reset code sent to email',
                },
            )

    def confirm_forgot_password(self, change_password: ConfirmForgotPasswordRequest):
        """
        Confirms a password reset request initiated by the user.

        :param change_password: The details of the password reset request.
        :type change_password: ConfirmForgotPasswordRequest

        :raises Exception: Bad request message if an error occurs during the password reset confirmation process.

        :return: A JSON response indicating the outcome of the password reset confirmation.
        :rtype: JSONResponse
        """
        try:
            self.client.confirm_forgot_password(
                ClientId=self.user_pool_client_id,
                Username=change_password.email,
                SecretHash=Utils.compute_secret_hash(
                    client_secret=self.client_secret,
                    user_name=change_password.email,
                    client_id=self.user_pool_client_id,
                ),
                ConfirmationCode=change_password.confirmationCode,
                Password=change_password.password,
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    'message': 'Password Changed Successfully',
                },
            )

    def change_password(self, change_password: ChangePasswordRequest):
        """
        Changes the password of a user.

        :param change_password: Object containing information required to change the password.
        :type change_password: ChangePasswordRequest

        :raises Exception: Bad request message if an error occurs during the password change process.

        :return: A JSON response indicating the outcome of the password change.
        :rtype: JSONResponse
        """
        try:
            self.client.change_password(
                PreviousPassword=change_password.previousPassword,
                ProposedPassword=change_password.proposedPassword,
                AccessToken=change_password.accessToken,
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    'message': 'Password Changed Successfully',
                },
            )

    def get_user(self, username: str):
        """
        Retrieves user information associated with the specified username.

        :param username: The username of the user to retrieve.
        :type username: str

        :raises Exception: If an error occurs during the user retrieval process.

        :return: The response containing user information if the operation is successful.
        :rtype: dict or None
        """
        try:
            response = self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=username)
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            return None
        else:
            return response

    def invite_admin(self, invite_admin: AdminIn):
        """
        Invites a new admin to the system.

        :param invite_admin: Object containing details of the admin to invite.
        :type invite_admin: AdminIn

        :raises Exception: Bad request message if an error occurs during the admin invitation process.

        :return: A JSON response indicating the outcome of the admin invitation.
        :rtype: JSONResponse
        """
        try:
            username = invite_admin.email
            user = self.get_user(username)
            if user is None:
                created_user = self.client.admin_create_user(
                    UserPoolId=self.user_pool_id,
                    Username=username,
                    TemporaryPassword=CommonConstants.TEMPORARY_PASSWORD,
                    ForceAliasCreation=False,
                    MessageAction='SUPPRESS',
                )
                user = created_user.get('User')

            self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=UserRoles.ADMIN.value,
            )

            # create a new admin
            sub = user.get('Username')
            created_admin = self.admin_uc.create_admin(admin_in=invite_admin, sub=sub)
            if isinstance(created_admin, JSONResponse):
                return created_admin

            # send email
            self.email_uc.send_admin_invitation_email(
                email=username,
                temp_password=CommonConstants.TEMPORARY_PASSWORD,
            )

        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    'message': 'User invited successfully',
                },
            )

    def update_temp_password(self, update_temp_password: UpdateTemporaryPasswordRequest):
        """
        Updates the temporary password of a user.

        :param update_temp_password: Object containing information required to update the temporary password.
        :type update_temp_password: UpdateTemporaryPasswordRequest

        :raises Exception: Bad request message if an error occurs during the temporary password update process.

        :return: A JSON response indicating the outcome of the temporary password update.
        :rtype: JSONResponse
        """
        try:
            response = self.login(
                login_details=Login(
                    email=update_temp_password.email,
                    password=update_temp_password.prevPassword,
                )
            )
            if not isinstance(response, Challenge):
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={
                        'message': 'Invalid credentials',
                    },
                )

            session = response.session
            self.client.respond_to_auth_challenge(
                ClientId=self.user_pool_client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=session,
                ChallengeResponses={
                    'USERNAME': update_temp_password.email,
                    'NEW_PASSWORD': update_temp_password.newPassword,
                    'SECRET_HASH': Utils.compute_secret_hash(
                        client_secret=self.client_secret,
                        user_name=update_temp_password.email,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )

            user = self.get_user(update_temp_password.email)
            sub = user.get('Username')
            self.admin_uc.update_admin(
                admin_id=sub,
                admin_in=AdminPatch(isConfirmed=True),
            )

        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    'message': 'Password Changed Successfully',
                },
            )

    def delete_admin(self, admin_id: str) -> Union[None, JSONResponse]:
        """
        Deletes an admin from the system.

        :param admin_id: The ID of the admin to delete.
        :type admin_id: str

        :raises Exception: Bad request message if an error occurs during the admin deletion process.

        :return: None if the deletion is successful, otherwise a JSON response indicating the error.
        :rtype: None or JSONResponse
        """
        try:
            self.client.admin_delete_user(UserPoolId=self.user_pool_id, Username=admin_id)
            return self.admin_uc.delete_admin(admin_id=admin_id)

        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={'message': message})
