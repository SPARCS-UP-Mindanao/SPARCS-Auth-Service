import os
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Path
from starlette.responses import JSONResponse

from aws.cognito_settings import AccessUser, get_current_user
from constants.common_constants import CommonConstants
from model.admins.admin import AdminIn, AdminOut
from model.common import Message
from model.user import SignUpResponse, UpdateTemporaryPasswordRequest
from usecase.admin_usecase import AdminUseCase
from usecase.auth_usecase import AuthUsecase

admin_auth_router = APIRouter()


@admin_auth_router.post(
    "/invite",
    response_model=SignUpResponse,
    responses={
        500: {"model": Message, "description": "Internal Server Error"},
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
    invite_admin_request: AdminIn,
    current_user: AccessUser = Depends(get_current_user),
):
    """
    Invite a new admin to the system.

    :param invite_admin_request: The details of the admin to invite.
    :type invite_admin_request: AdminIn

    :param current_user: The currently authenticated user.
    :type current_user: AccessUser

    :return: Unauthorized if the current user is not an admin, otherwise the response to the sign-up request.
    :rtype: JSONResponse
    """
    _ = current_user
    if os.getenv("CURRENT_USER_IS_ADMIN", "") != "True":
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={
                "message": "Unauthorized",
            },
        )

    auth_uc = AuthUsecase()
    return auth_uc.invite_admin(invite_admin_request)


@admin_auth_router.post(
    "/update-password",
    response_model=Message,
    responses={
        500: {"model": Message, "description": "Internal Server Error"},
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


@admin_auth_router.get(
    "/current-user",
    response_model=AccessUser,
    responses={
        404: {"model": Message, "description": "Admin not found"},
        500: {"model": Message, "description": "Internal server error"},
    },
    summary="Get Current user",
)
@admin_auth_router.get(
    "/current-user/",
    response_model=AccessUser,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def get_current_user_admin(
    current_user: AccessUser = Depends(get_current_user),
):
    """
    Get information about the current user.

    :param current_user: The currently authenticated user.
    :type current_user: AccessUser

    :return: The current user.
    :rtype: AccessUser
    """
    return current_user


@admin_auth_router.get(
    "",
    response_model=List[AdminOut],
    responses={
        404: {"model": Message, "description": "Admin not found"},
        500: {"model": Message, "description": "Internal server error"},
    },
    summary="Get Admins",
)
@admin_auth_router.get(
    "/",
    response_model=List[AdminOut],
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def get_admins(
    current_user: AccessUser = Depends(get_current_user),
):
    """
    Get a list of all admins in the current database.

    :param current_user: The currently authenticated user.
    :type current_user: AccessUser

    :return: A list of admin records, otherwise an error message for unauthorized access.
    :rtype: List[AdminOut] or JSONResponse

    :responses:
        - 200: List of admins retrieved successfully
        - 404: Admin not found
        - 500: Internal server error
    """
    _ = current_user
    if os.getenv("CURRENT_USER_IS_ADMIN") != "True":
        return JSONResponse(
            status_code=HTTPStatus.FORBIDDEN,
            content={"message": "Unauthorized"},
        )

    admin_uc = AdminUseCase()
    return admin_uc.get_admins()


@admin_auth_router.get(
    "/{entryId}",
    response_model=AdminOut,
    responses={
        404: {"model": Message, "description": "Admin not found"},
        500: {"model": Message, "description": "Internal server error"},
    },
    summary="Get Admin",
)
@admin_auth_router.get(
    "/{entryId}/",
    response_model=AdminOut,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def get_admin(
    entry_id: str = Path(..., title="admin Id", alias=CommonConstants.ENTRY_ID),
    current_user: AccessUser = Depends(get_current_user),
):
    """
    Get details of a single admin from the current database.

    :param entry_id: The ID of the admin to retrieve.
    :type entry_id: str

    :param current_user: The currently authenticated user.
    :type current_user: AccessUser

    :return: The details of the admin, otherwise an error message for unauthorized access.
    :rtype: AdminOut or JSONResponse

    :responses:
        - 200: Admin retrieved successfully
        - 404: Admin not found
        - 500: Internal server error
    """
    _ = current_user
    if os.getenv("CURRENT_USER_IS_ADMIN") != "True":
        return JSONResponse(
            status_code=HTTPStatus.FORBIDDEN,
            content={"message": "Unauthorized"},
        )

    admins_uc = AdminUseCase()
    return admins_uc.get_admin(entry_id)


@admin_auth_router.put(
    "/{entryId}",
    response_model=AdminOut,
    responses={
        400: {"model": Message, "description": "Bad request"},
        404: {"model": Message, "description": "Admin not found"},
        500: {"model": Message, "description": "Internal server error"},
    },
    summary="Update Admin",
)
@admin_auth_router.put(
    "/{entryId}/",
    response_model=AdminOut,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    include_in_schema=False,
)
def update_admin(
    admin: AdminIn,
    entry_id: str = Path(..., title="Admin Id", alias=CommonConstants.ENTRY_ID),
    current_user: AccessUser = Depends(get_current_user),
):
    """
    Update an admin's details in the current database.

    :param entry_id: The ID of the admin to update.
    :type entry_id: str

    :param admin: New details for the admin.
    :type admin: AdminIn

    :param current_user: The currently authenticated user.
    :type current_user: AccessUser

    :return: Updated details of the admin, otherwise an error message for unauthorized access.
    :rtype: AdminOut or JSONResponse

    :responses:
        - 200: Admin updated successfully
        - 400: Bad request
        - 404: Admin not found
        - 500: Internal server error
    """
    _ = current_user
    if os.getenv("CURRENT_USER_IS_ADMIN") != "True":
        return JSONResponse(
            status_code=HTTPStatus.FORBIDDEN,
            content={"message": "Unauthorized"},
        )

    admin_uc = AdminUseCase()
    return admin_uc.update_admin(entry_id, admin)


@admin_auth_router.delete(
    "/{entryId}",
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        204: {"description": "Admin entry deletion success", "content": None},
    },
    summary="Delete Admin",
)
@admin_auth_router.delete(
    "/{entryId}/",
    status_code=HTTPStatus.NO_CONTENT,
    include_in_schema=False,
)
def delete_admin(
    entry_id: str = Path(..., title="admin Id", alias=CommonConstants.ENTRY_ID),
    current_user: AccessUser = Depends(get_current_user),
):
    """
    Update an admin's details in the current database.

    :param entry_id: The ID of the admin to update.
    :type entry_id: str

    :param admin: New details for the admin.
    :type admin: AdminIn

    :param current_user: The currently authenticated user.
    :type current_user: AccessUser

    :return: Updated details of the admin, otherwise an error message for unauthorized access.
    :rtype: AdminOut or JSONResponse

    :responses:
        - 200: Admin updated successfully
        - 400: Bad request
        - 404: Admin not found
        - 500: Internal server error
    """
    _ = current_user
    if os.getenv("CURRENT_USER_IS_ADMIN") != "True":
        return JSONResponse(
            status_code=HTTPStatus.FORBIDDEN,
            content={"message": "Unauthorized"},
        )

    admin_uc = AuthUsecase()
    return admin_uc.delete_admin(entry_id)
