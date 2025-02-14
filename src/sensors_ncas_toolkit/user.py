"""Handle requests about the user from the Sensors API

This module contains the UserInfo class, which is used to handle requests to the
Sensors API, including getting user information and user permission groups.
"""

import requests
from .core import CoreApi

from typing import Any, Optional, override


class UserInfo(CoreApi):
    """Manages requests about the user.

    Class that deals with requests to the Sensors API about devices.

    Attributes:
        base_url: The base url of the Sensors API
        headers: The headers of the request
        api_key: The api key to authenticate the request
        user_info: The json object containing information about the user
        user_groups: List of groups the user is part of
    """
    @override
    def __init__(self, api_key: Optional[None] = None) -> None:
        super().__init__(api_key)
        self.user_info = self.get_user_info()
        self.user_groups = self.get_user_groups()


    def _check_user_api_key(self, verbose=True) -> bool:
        """Check if API key exists.

        Args:
            verbose: Print warning message if no API key exists

        Returns:
            Boolean for API key existence.
        """
        if self.api_key is None:
            if verbose:
                print("[WARNING]: No user API key found.")
            return False
        return True


    def get_user_info(self) -> Optional[dict[str, Any]]:
        """Get basic information on the user.

        Gets basic information about the user using the API key in the class attribute.

        Returns:
            Dictionary with basic user information.

        Raises:
            Exception: If the request fails, raises an exception with the status code
        """
        if not self._check_user_api_key():
            return None

        response = requests.get(
            f"{self.base_url}/user-info",
            headers = self.headers,
        )
        if response.status_code != 200:
            msg = f"Failed to get user info. Status code: {response.status_code}"
            raise Exception(msg)
        return response.json()


    def get_all_groups(self) -> dict[str, Any]:
        """Get all permission groups.

        Returns:
            Dictionary with information on all permission groups.

        Raises:
            Exception: If the request fails, raises an exception with the status code
        """
        response = requests.get(
            f"{self.base_url}/permission-groups",
            headers = self.headers,
        )
        if response.status_code != 200:
            msg = f"Failed to get groups. Status code: {response.status_code}"
            raise Exception(msg)
        return response.json()


    def get_user_groups(self) -> Optional[list[dict[str, Any]]]:
        """Get permission groups user is part of.

        Using the API key in the class attribute, gets all permission groups that the
        user is a member of.

        Returns:
            Dictionary with information on all permission groups.

        Raises:
            Exception: If the request fails, raises an exception with the status code
        """
        if self.user_info is None:
            if self._check_user_api_key():
                self.user_info = self.get_user_info()
            else:
                return None

        all_perm_groups = self.get_all_groups()
        user_group_ids = self.user_info["data"]["attributes"]["member"]
        user_group_list = []
        for group in all_perm_groups["data"]:
            if group["id"] in user_group_ids:
                user_group_list.append(group)
        return user_group_list

    



