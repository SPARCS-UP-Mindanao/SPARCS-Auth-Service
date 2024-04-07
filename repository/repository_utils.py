import json
from copy import deepcopy
from typing import Tuple

from pynamodb.attributes import MapAttribute
from pynamodb.models import Model

from constants.common_constants import CommonConstants


class RepositoryUtils:
    @staticmethod
    def get_update(old_data: dict, new_data: dict) -> Tuple[bool, dict]:
        """
        Compares old data with new data and returns whether there are updates along with the updated data.

        :param old_data: The old data.
        :type old_data: dict

        :param new_data: The updated data.
        :type new_data: dict

        :return: A tuple containing whether there are updates and the updated data.
        :rtype: Tuple[bool, dict]
        """
        excluded_comparison_keys = deepcopy(CommonConstants.EXCLUDE_COMPARISON_KEYS)

        # copy old_data
        old_data_copy = deepcopy(old_data)
        for key in excluded_comparison_keys:
            old_data_copy.pop(key, None)

        # set updated_data
        updated_data = deepcopy(old_data_copy)
        RepositoryUtils.update_nested_dict(updated_data, new_data)
        has_update = updated_data != old_data_copy

        # Change to MapAttribute
        updated_data = RepositoryUtils.items_to_map_attr(updated_data)

        return has_update, updated_data

    @staticmethod
    def update_nested_dict(old_dict: dict, new_data: dict):
        """
        Updates a nested dictionary with values from another dictionary.

        :param old_dict: The dictionary to update.
        :type old_dict: dict

        :param new_data: The dictionary containing the new values.
        :type new_data: dict

        :return: The updated dictionary.
        :rtype: dict
        """
        for key, val in new_data.items():
            if isinstance(val, dict):
                try:
                    RepositoryUtils.update_nested_dict(old_dict[key], val)
                except KeyError:
                    old_dict[key] = {}
                    RepositoryUtils.update_nested_dict(old_dict[key], val)
            elif val is not None or key in old_dict:
                old_dict[key] = val

        return old_dict

    @staticmethod
    def items_to_map_attr(hub_dict: dict) -> dict:
        """
        Converts items in a dictionary to MapAttribute objects recursively.

        :param hub_dict: The dictionary to convert.
        :type hub_dict: dict

        :return: The dictionary with items converted to MapAttribute objects.
        :rtype: dict
        """
        tmp_dict = {}
        for key, val in hub_dict.items():
            if isinstance(val, dict):
                new_dict = RepositoryUtils.items_to_map_attr(val)
                tmp_dict[key] = MapAttribute(**new_dict)
            else:
                tmp_dict[key] = val
        return tmp_dict

    @staticmethod
    def db_model_to_dict(model: Model) -> dict:
        """
        Converts a database model object to a dictionary representation.

        :param model: The database model object.
        :type model: Model

        :return: The dictionary representation of the database model object.
        :rtype: dict
        """
        json_str = model.to_json()
        hub_dict = json.loads(json_str)
        return hub_dict

    @staticmethod
    def load_data(pydantic_schema_in, exclude_unset=False):
        """
        Loads data from a Pydantic schema object into a dictionary.

        :param pydantic_schema_in: The Pydantic schema object.
        :type pydantic_schema_in: pydantic.BaseModel

        :param exclude_unset: Whether to exclude unset values.
        :type exclude_unset: bool

        :return: The dictionary representation of the Pydantic schema object.
        :rtype: dict
        """
        return json.loads(pydantic_schema_in.json(exclude_unset=exclude_unset))
