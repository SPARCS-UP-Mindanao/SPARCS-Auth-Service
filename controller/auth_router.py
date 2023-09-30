from fastapi import APIRouter

from model.user import (
    AuthResponse,
    ConfirmSignUp,
    Login,
    LogOutRequest,
    RefreshTokenRequest,
    SignUp,
    SignUpResponse,
)
from usecase.auth_usecase import AuthUsecase

auth_router = APIRouter(
    tags=["Auth"],
)


@auth_router.post(
    "/signup",
    status_code=200,
    response_model=SignUpResponse,
    summary="Register User",
)
@auth_router.post(
    "/signup/",
    status_code=200,
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
    status_code=200,
    response_model=AuthResponse,
    summary="Login User",
)
@auth_router.post(
    "/login/",
    status_code=200,
    response_model=AuthResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def login(login_details: Login):
    auth_uc = AuthUsecase()
    return auth_uc.login(login_details)


@auth_router.post(
    "/refresh",
    status_code=200,
    response_model=AuthResponse,
    summary="Refresh Token",
)
@auth_router.post(
    "/refresh/",
    status_code=200,
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
    status_code=200,
    response_model=dict,
    summary="Confirm User",
)
@auth_router.post(
    "/confirm/",
    status_code=200,
    response_model=dict,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def confirm(confirm_signup: ConfirmSignUp):
    auth_uc = AuthUsecase()
    return auth_uc.confirm_signup(confirm_signup)


@auth_router.post(
    "/logout",
    status_code=200,
    response_model=dict,
    summary="Logout User",
)
@auth_router.post(
    "/logout/",
    status_code=200,
    response_model=dict,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def logout(log_out_request: LogOutRequest):
    auth_uc = AuthUsecase()
    return auth_uc.sign_out(accessToken=log_out_request.accessToken)
