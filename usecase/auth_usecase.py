import logging
import os
from http import HTTPStatus

from boto3 import client as boto3_client
from starlette.responses import JSONResponse

from constants.common_constants import CommonConstants, UserRoles
from model.user import (
    AuthResponse,
    Challenge,
    ChangePasswordRequest,
    ConfirmForgotPasswordRequest,
    ConfirmSignUp,
    InviteAdminRequest,
    Login,
    RefreshTokenRequest,
    SignUp,
    SignUpResponse,
    UpdateTemporaryPasswordRequest,
)
from utils.utils import Utils


class AuthUsecase:
    def __init__(self) -> None:
        self.client = boto3_client('cognito-idp', region_name=os.environ['REGION'])
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.user_pool_client_id = os.getenv('USER_POOL_CLIENT_ID')
        self.client_secret = Utils.get_secret(os.getenv('CLIENT_SECRET_NAME'))

    def signup(self, sign_up_details: SignUp):
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
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return res

    def confirm_signup(self, confirm_signup: ConfirmSignUp):
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
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "User confirmed successfully",
                },
            )

    def login(self, login_details: Login):
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
                            "message": "Invalid credentials",
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
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return auth_response

    def refresh(self, refresh_token_request: RefreshTokenRequest):
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
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})

    def sign_out(self, accessToken: str):
        try:
            self.client.global_sign_out(AccessToken=accessToken)
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "User logged out successfully",
                },
            )

    def forgot_password(self, email: str):
        try:
            self.client.forgot_password(
                ClientId=self.user_pool_client_id,
                Username=email,
                SecretHash=Utils.compute_secret_hash(
                    client_secret=self.client_secret, user_name=email, client_id=self.user_pool_client_id
                ),
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Password reset code sent to email",
                },
            )

    def confirm_forgot_password(self, change_password: ConfirmForgotPasswordRequest):
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
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Password Changed Successfully",
                },
            )

    def change_password(self, change_password: ChangePasswordRequest):
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
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Password Changed Successfully",
                },
            )

    def get_user(self, username: str):
        try:
            response = self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=username)
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            return None
        else:
            return response

    def invite_admin(self, invite_admin: InviteAdminRequest):
        if os.getenv('CURRENT_USER_IS_ADMIN', '') != 'True':
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={
                    "message": "Unauthorized",
                },
            )

        try:
            username = invite_admin.email
            user = self.get_user(username)
            if user is None:
                self.client.admin_create_user(
                    UserPoolId=self.user_pool_id,
                    Username=username,
                    TemporaryPassword=CommonConstants.TEMPORARY_PASSWORD,
                    ForceAliasCreation=False,
                    DesiredDeliveryMediums=['EMAIL'],
                )

            self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id, Username=username, GroupName=UserRoles.ADMIN.value
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "User invited successfully",
                },
            )

    def update_temp_password(self, update_temp_password: UpdateTemporaryPasswordRequest):
        try:
            self.client.respond_to_auth_challenge(
                ClientId=self.user_pool_client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=update_temp_password.session,
                ChallengeResponses={
                    'USERNAME': update_temp_password.email,
                    'NEW_PASSWORD': update_temp_password.password,
                    'SECRET_HASH': Utils.compute_secret_hash(
                        client_secret=self.client_secret,
                        user_name=update_temp_password.email,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )
        except Exception as e:
            err_msg = str(e)
            logging.error(err_msg)
            message = Utils.strip_error_message(err_msg)
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": message})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Password Changed Successfully",
                },
            )
