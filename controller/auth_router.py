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
    "/signup",
    response_model=SignUpResponse,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Register User",
)
@auth_router.post(
    "/signup/",
    response_model=SignUpResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def signup(signup_details: SignUp):
    auth_uc = AuthUsecase()
    return auth_uc.signup(signup_details)


@auth_router.post(
    "/login",
    response_model=Union[AuthResponse, Challenge],
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Login User",
)
@auth_router.post(
    "/login/",
    response_model=Union[AuthResponse, Challenge],
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def login(login_details: Login):
    auth_uc = AuthUsecase()
    return auth_uc.login(login_details)


@auth_router.post(
    "/refresh",
    response_model=AuthResponse,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Refresh Token",
)
@auth_router.post(
    "/refresh/",
    response_model=AuthResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def refresh(refreshToken: RefreshTokenRequest):
    auth_uc = AuthUsecase()
    return auth_uc.refresh(refreshToken)


@auth_router.post(
    "/confirm",
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Confirm User",
)
@auth_router.post(
    "/confirm/",
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def confirm(confirm_signup: ConfirmSignUp):
    auth_uc = AuthUsecase()
    return auth_uc.confirm_signup(confirm_signup)


@auth_router.post(
    "/logout",
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Logout User",
)
@auth_router.post(
    "/logout/",
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def logout(log_out_request: LogOutRequest):
    auth_uc = AuthUsecase()
    return auth_uc.sign_out(accessToken=log_out_request.accessToken)


@auth_router.post(
    "/forgot-password",
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Forgot Password",
)
@auth_router.post(
    "/forgot-password/",
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def forgot_password(req: ForgotPasswordRequest):
    auth_uc = AuthUsecase()
    return auth_uc.forgot_password(req.email)


@auth_router.post(
    "/confirm-forgot-password",
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Change Password",
)
@auth_router.post(
    "/confirm-forgot-password/",
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def confirm_forgot_password(req: ConfirmForgotPasswordRequest):
    auth_uc = AuthUsecase()
    return auth_uc.confirm_forgot_password(req)


@auth_router.post(
    "/change-password",
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Change Password",
)
@auth_router.post(
    "/change-password/",
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def change_password(req: ChangePasswordRequest):
    auth_uc = AuthUsecase()
    return auth_uc.change_password(req)
