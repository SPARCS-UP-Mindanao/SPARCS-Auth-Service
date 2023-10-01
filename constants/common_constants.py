from enum import Enum


class CommonConstants:
    DOMAIN_NAME = 'sparcsup.com'
    TEMPORARY_PASSWORD = 'Sparcsup123#'


class UserRoles(Enum):
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'
