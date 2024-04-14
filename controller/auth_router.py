from typing import Union

from fastapi import APIRouter

from model.common import Message
from model.user import (
    AuthResponse,
    Challenge,
    ChangePasswordRequest,
    ConfirmForgotPasswordRequest,
    ConfirmSignUp,
    ForgotPasswordRequest,
    Login,
    LogOutRequest,
    RefreshTokenRequest,
    SignUp,
    SignUpResponse,
)
from usecase.auth_usecase import AuthUsecase

auth_router = APIRouter()


@auth_router.post(
    '/signup',
    response_model=SignUpResponse,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Register User',
)
@auth_router.post(
    '/signup/',
    response_model=SignUpResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def signup(signup_details: SignUp):
    """
    Calls method to sign up a user.

    :param signup_details: The details of the user to sign up.
    :type signup_details: SignUp

    :return: The response to the sign-up request.
    :rtype: SignUpResponse
    """
    auth_uc = AuthUsecase()
    return auth_uc.signup(signup_details)


@auth_router.post(
    '/login',
    response_model=Union[AuthResponse, Challenge],
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Login User',
)
@auth_router.post(
    '/login/',
    response_model=Union[AuthResponse, Challenge],
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def login(login_details: Login):
    """
    Calls method to log in a user.

    :param login_details: The details of the user to log in.
    :type login_details: Login

    :return: The response to the login request.
    :rtype: AuthResponse or Challenge
    """
    auth_uc = AuthUsecase()
    return auth_uc.login(login_details)


@auth_router.post(
    '/refresh',
    response_model=AuthResponse,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Refresh Token',
)
@auth_router.post(
    '/refresh/',
    response_model=AuthResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def refresh(refreshToken: RefreshTokenRequest):
    """
    Calls the method to refresh the access token using a refresh token.

    :param refreshToken: Object containing the refresh token.
    :type refreshToken: RefreshTokenRequest

    :return: The response to the refresh token request with the new access token, refresh token and username as payload.
    :rtype: JSONResponse
    """
    auth_uc = AuthUsecase()
    return auth_uc.refresh(refreshToken)


@auth_router.post(
    '/confirm',
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Confirm User',
)
@auth_router.post(
    '/confirm/',
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def confirm(confirm_signup: ConfirmSignUp):
    """
    Confirms the sign-up process for a user.

    :param confirm_signup: Object containing details required for sign-up confirmation.
    :type confirm_signup: ConfirmSignUp

    :return: The response to the sign-up confirmation request.
    :rtype: JSONResponse
    """
    auth_uc = AuthUsecase()
    return auth_uc.confirm_signup(confirm_signup)


@auth_router.post(
    '/logout',
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Logout User',
)
@auth_router.post(
    '/logout/',
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def logout(log_out_request: LogOutRequest):
    """
    Logs out a user from the system.

    :param log_out_request: Object containing the access token of the user to log out.
    :type log_out_request: LogOutRequest

    :return: The response to the log out request.
    :rtype: JSONResponse
    """
    auth_uc = AuthUsecase()
    return auth_uc.sign_out(accessToken=log_out_request.accessToken)


@auth_router.post(
    '/forgot-password',
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Forgot Password',
)
@auth_router.post(
    '/forgot-password/',
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def forgot_password(req: ForgotPasswordRequest):
    """
    Initiates the password reset process for a user.

    :param req: Object containing the email address of the user requesting password reset.
    :type req: ForgotPasswordRequest

    :return: The response to the password reset request.
    :rtype: JSONResponse
    """
    auth_uc = AuthUsecase()
    return auth_uc.forgot_password(req.email)


@auth_router.post(
    '/confirm-forgot-password',
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Change Password',
)
@auth_router.post(
    '/confirm-forgot-password/',
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def confirm_forgot_password(req: ConfirmForgotPasswordRequest):
    """
    Confirms the password reset process for a user.

    :param req: Object containing the email address and new password of the user.
    :type req: ConfirmForgotPasswordRequest

    :return: The response to the password reset confirmation request.
    :rtype: JSONResponse
    """
    auth_uc = AuthUsecase()
    return auth_uc.confirm_forgot_password(req)


@auth_router.post(
    '/change-password',
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary='Change Password',
)
@auth_router.post(
    '/change-password/',
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def change_password(req: ChangePasswordRequest):
    """
    Handles the request to change the password of a user.

    :param req: Object containing the old and new passwords of the user.
    :type req: ChangePasswordRequest

    :return: The response to the password change request.
    :rtype: JSONResponse
    """
    auth_uc = AuthUsecase()
    return auth_uc.change_password(req)
