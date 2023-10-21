from fastapi import APIRouter, Depends

from aws.cognito_settings import AccessUser, get_current_user
from model.common import Message
from model.user import (
    InviteAdminRequest,
    SignUpResponse,
    UpdateTemporaryPasswordRequest,
)
from usecase.auth_usecase import AuthUsecase

admin_auth_router = APIRouter()


@admin_auth_router.post(
    "/invite",
    response_model=SignUpResponse,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Register User",
)
@admin_auth_router.post(
    "/invite/",
    response_model=SignUpResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def invite_admin(
    invite_admin_request: InviteAdminRequest,
    current_user: AccessUser = Depends(get_current_user),
):
    _ = current_user
    auth_uc = AuthUsecase()
    return auth_uc.invite_admin(invite_admin_request)


@admin_auth_router.post(
    "/update-password",
    response_model=Message,
    responses={
        500: {'model': Message, 'description': 'Internal Server Error'},
    },
    summary="Change Password",
)
@admin_auth_router.post(
    "/update-password/",
    response_model=Message,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def update_temp_password(req: UpdateTemporaryPasswordRequest):
    auth_uc = AuthUsecase()
    return auth_uc.update_temp_password(req)
