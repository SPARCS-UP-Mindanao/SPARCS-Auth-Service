from fastapi import APIRouter
from model.user import SignUp, Login, RefreshTokenRequest, ConfirmSignUp
from usecase.auth_usecase import AuthUsecase

auth_router = APIRouter(
    tags=["Auth"],
)


@auth_router.post(
    "/signup",
    status_code=200,
    response_model=dict,
    summary="Register User",
)
@auth_router.post(
    "/signup/",
    status_code=200,
    response_model=dict,
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
    response_model=dict,
    summary="Login User",
)
@auth_router.post(
    "/login/",
    status_code=200,
    response_model=dict,
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
    response_model=dict,
    summary="Refresh Token",
)
@auth_router.post(
    "/refresh/",
    status_code=200,
    response_model=dict,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def refresh(refresh_token: RefreshTokenRequest):
    auth_uc = AuthUsecase()
    return auth_uc.refresh(refresh_token)


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
def logout(access_token: str):
    auth_uc = AuthUsecase()
    return auth_uc.sign_out(access_token=access_token)
