from enum import Enum


class UserRoles(str, Enum):
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'


class EntryStatus(str, Enum):
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'


class CommonConstants:
    DOMAIN_NAME = 'sparcsup.com'
    TEMPORARY_PASSWORD = 'Sparcsup123#'

    # DB Constants
    CLS = 'cls'
    HASH_KEY = 'hashKey'
    RANGE_KEY = 'rangeKey'

    LATEST_VERSION = 'latestVersion'
    ENTRY_STATUS = 'entryStatus'
    CREATE_DATE = 'createDate'
    UPDATE_DATE = 'updateDate'
    CREATED_BY = 'createdBy'
    UPDATED_BY = 'updatedBy'

    ENTRY_ID = 'entryId'
    EVENT_ID = 'eventId'
    ADMIN_ID = 'adminId'
    REGISTRATION_ID = 'registrationId'

    # Exclude to Comparison Keys
    EXCLUDE_COMPARISON_KEYS = [
        CLS,
        HASH_KEY,
        RANGE_KEY,
        ENTRY_STATUS,
        ENTRY_ID,
        CREATE_DATE,
        UPDATE_DATE,
        CREATED_BY,
        UPDATED_BY,
        LATEST_VERSION,
    ]


class EmailType(str, Enum):
    REGISTRATION_EMAIL = 'registrationEmail'
    CONFIRMATION_EMAIL = 'confirmationEmail'
    EVALUATION_EMAIL = 'evaluationEmail'
    EVENT_CREATION_EMAIL = 'eventCreationEmail'
