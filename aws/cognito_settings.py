import os

from fastapi import Depends, HTTPException
from fastapi_cloudauth import Cognito
from pydantic import BaseModel, Field

from constants.common_constants import UserRoles


class AccessUser(BaseModel):
    sub: str
    groups: list = Field([], alias='cognito:groups')
    username: str = None


__auth = Cognito(
    region=os.environ['REGION'],
    userPoolId=os.environ['USER_POOL_ID'],
    client_id=os.environ['USER_POOL_CLIENT_ID'],
)


def get_current_user(
    current_user: AccessUser = Depends(__auth.claim(AccessUser)),
) -> AccessUser:
    """
    Retrieves information about the current user, such as their UUID (referred to as 'sub') and the groups they belong
    to, and stores this information in environment variables.

    :param current_user: An object representing the current user.
    :type current_user: AccessUser

    :raises HTTPException: The user is not authenticated.

    :return: The current user.
    :rtype: AccessUser
    """

    if not current_user.username:
        raise HTTPException(status_code=401, detail='Invalid access token')

    os.environ['CURRENT_USER'] = current_user.sub
    is_super_admin = UserRoles.SUPER_ADMIN.value in current_user.groups
    os.environ['CURRENT_USER_IS_ADMIN'] = str(is_super_admin)
    message = f'CurrentUser: {current_user.sub} {current_user.groups}'
    print(message)
    return current_user
