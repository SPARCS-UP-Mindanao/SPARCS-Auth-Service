import logging
import os
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus
from typing import List, Tuple

from pynamodb.connection import Connection
from pynamodb.exceptions import (
    DeleteError,
    PutError,
    PynamoDBConnectionError,
    QueryError,
    TableDoesNotExist,
    TransactWriteError,
)
from pynamodb.transactions import TransactWrite

from constants.common_constants import EntryStatus
from model.admins.admin import Admin, AdminIn
from repository.repository_utils import RepositoryUtils


class AdminsRepository:
    def __init__(self) -> None:
        """
        Initialize the AdminsRepository.

        This class is responsible for managing the interaction with the Admin entities in the database.

        Attributes:
        - self.core_obj (str): The core object representing Admin entities.
        - self.current_date (str): The current date in ISO format.
        - self.latest_version (int): The latest version number.
        - self.conn (Connection): The connection to the DynamoDB database.

        """
        self.core_obj = 'Admin'
        self.current_date = datetime.utcnow().isoformat()
        self.latest_version = 0
        self.conn = Connection(region=os.getenv('REGION'))

    def store_admin(self, admin_in: AdminIn, sub: str) -> Tuple[HTTPStatus, Admin, str]:
        """
        Store an Admin entity in the database.

        :param admin_in: The data for the Admin entity.
        :type admin_in: AdminIn

        :param sub: The ID of the Admin entity.
        :type sub: str

        :return: A tuple containing HTTP status, the stored Admin entity, and an error message if any.
        :rtype: Tuple[HTTPStatus, Admin, str]
        """
        data = RepositoryUtils.load_data(pydantic_schema_in=admin_in)
        range_key = f'v{self.latest_version}#{sub}'
        try:
            admin_entry = Admin(
                hashKey=self.core_obj,
                rangeKey=range_key,
                createDate=self.current_date,
                updateDate=self.current_date,
                createdBy=os.getenv('CURRENT_USER'),
                updatedBy=os.getenv('CURRENT_USER'),
                latestVersion=self.latest_version,
                entryStatus=EntryStatus.ACTIVE.value,
                entryId=sub,
                **data,
            )
            admin_entry.save()

        except PutError as e:
            message = f'Failed to save admin strategy form: {str(e)}'
            logging.error(f'[{self.core_obj} = {sub}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message
        except TableDoesNotExist as db_error:
            message = f'Error on Table, Please check config to make sure table is created: {str(db_error)}'
            logging.error(f'[{self.core_obj} = {sub}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message
        except PynamoDBConnectionError as db_error:
            message = f'Connection error occurred, Please check config(region, table name, etc): {str(db_error)}'
            logging.error(f'[{self.core_obj} = {sub}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message
        else:
            logging.info(f'[{self.core_obj} = {sub}]: Save Admins strategy data successful')
            return HTTPStatus.OK, admin_entry, None

    def query_admins(self, admin_id: str = None) -> Tuple[HTTPStatus, List[Admin], str]:
        """
        Query Admin entities from the database.

        :param admin_id: The ID of the Admin entity to query.
        :type admin_id: str

        :return: A tuple containing HTTP status, a list of queried Admin entities, and an error message if any.
        :rtype: Tuple[HTTPStatus, List[Admin], str]
        """
        try:
            if admin_id:
                range_key_prefix = f'v{self.latest_version}#{admin_id}'
                range_key_condition = Admin.rangeKey.__eq__(range_key_prefix)
            else:
                range_key_prefix = f'v{self.latest_version}#'
                range_key_condition = Admin.rangeKey.startswith(range_key_prefix)

            admin_entries = list(
                Admin.query(
                    hash_key=self.core_obj,
                    range_key_condition=range_key_condition,
                    filter_condition=Admin.entryStatus == EntryStatus.ACTIVE.value,
                )
            )
            if not admin_entries:
                if admin_id:
                    message = f'Admin with id {admin_id} not found'
                    logging.error(f'[{self.core_obj}={admin_id}] {message}')
                else:
                    message = 'No Admins found'
                    logging.error(f'[{self.core_obj}] {message}')

                return HTTPStatus.NOT_FOUND, None, message

        except QueryError as e:
            return self._extracted_from_query_admins_37('Failed to query admin: ', e, admin_id)
        except TableDoesNotExist as db_error:
            return self._extracted_from_query_admins_37(
                'Error on Table, Please check config to make sure table is created: ',
                db_error,
                admin_id,
            )
        except PynamoDBConnectionError as db_error:
            return self._extracted_from_query_admins_37(
                'Connection error occurred, Please check config(region, table name, etc): ',
                db_error,
                admin_id,
            )
        else:
            if admin_id:
                logging.info(f'[{self.core_obj}={admin_id}] Fetch Admin data successful')
                return HTTPStatus.OK, admin_entries[0], None

            logging.info(f'[{self.core_obj}={admin_id}] Fetch Admin data successful')
            return HTTPStatus.OK, admin_entries, None

    # TODO Rename this here and in `query_admins`
    def _extracted_from_query_admins_37(self, arg0, arg1, admin_id):
        message = f'{arg0}{str(arg1)}'
        logging.error(f'[{self.core_obj}={admin_id}] {message}')
        return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

    def update_admin(self, admin_entry: Admin, admin_in: AdminIn) -> Tuple[HTTPStatus, Admin, str]:
        """
        Update an Admin entity in the database.

        :param admin_entry: The existing Admin entity to update.
        :type admin_entry: Admin

        :param admin_in: The new data for the Admin entity.
        :type admin_in: AdminIn

        :return: A tuple containing HTTP status, the updated Admin entity, and an error message if any.
        :rtype: Tuple[HTTPStatus, Admin, str]
        """
        current_version = admin_entry.latestVersion
        new_version = current_version + 1

        data = RepositoryUtils.load_data(pydantic_schema_in=admin_in, exclude_unset=True)
        has_update, updated_data = RepositoryUtils.get_update(
            old_data=RepositoryUtils.db_model_to_dict(admin_entry), new_data=data
        )
        if not has_update:
            return HTTPStatus.OK, admin_entry, 'no update'
        try:
            with TransactWrite(connection=self.conn) as transaction:
                # Update Entry -----------------------------------------------------------------------------
                # check if there's update or none
                updated_data.update(
                    updateDate=self.current_date,
                    latestVersion=new_version,
                )
                actions = [getattr(Admin, k).set(v) for k, v in updated_data.items()]
                transaction.update(admin_entry, actions=actions)

                # Store Old Entry --------------------------------------------------------------------------
                old_admin_entry = deepcopy(admin_entry)
                old_admin_entry.rangeKey = admin_entry.rangeKey.replace('v0#', f'v{new_version}#')
                old_admin_entry.latestVersion = current_version
                old_admin_entry.updatedBy = old_admin_entry.updatedBy or os.getenv('CURRENT_USER')
                transaction.save(old_admin_entry)

            admin_entry.refresh()
            logging.info(f'[{admin_entry.rangeKey}] ' f'Update Admin data successful')
            return HTTPStatus.OK, admin_entry, ''

        except TransactWriteError as e:
            message = f'Failed to update admin data: {str(e)}'
            logging.error(f'[{admin_entry.rangeKey}] {message}')

            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

    def delete_admin(self, admin_entry: Admin) -> Tuple[HTTPStatus, str]:
        """
        Delete an Admin entity in the database.

        :param admin_entry: The Admin entity to delete.
        :type admin_entry: Admin

        :return: A tuple containing HTTP status and an error message if any.
        :rtype: Tuple[HTTPStatus, str]
        """

        try:
            # create new entry with old data
            current_version = admin_entry.latestVersion
            new_version = current_version + 1
            old_admin_entry = deepcopy(admin_entry)
            old_admin_entry.rangeKey = admin_entry.rangeKey.replace('v0#', f'v{new_version}#')
            old_admin_entry.updatedBy = old_admin_entry.updatedBy or os.getenv('CURRENT_USER')
            old_admin_entry.save()

            # set entry status to deleted
            admin_entry.updateDate = self.current_date
            admin_entry.updatedBy = os.getenv('CURRENT_USER')
            admin_entry.latestVersion = new_version
            admin_entry.entryStatus = EntryStatus.DELETED.value
            admin_entry.save()

            logging.info(f'[{admin_entry.rangeKey}] ' f'Deleted Admin data successful')
            return HTTPStatus.OK, None
        except DeleteError as e:
            message = f'Failed to delete Admin data: {str(e)}'
            logging.error(f'[{admin_entry.rangeKey}] {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, message
