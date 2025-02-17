"""Handle requests about contacts in the Sensors API

This module contains the Contacts class, which is used to handle requests to the
Sensors API.
"""

import requests
from .core import CoreApi

from typing import Any, Optional, override, Union


class Contacts(CoreApi):
    """Manages requests about the user.

    Class that deals with requests to the Sensors API about devices.

    Attributes:
        base_url: The base url of the Sensors API
        headers: The headers of the request
        api_key: The api key to authenticate the request
        all_contacts: The json object containing information about all contacts in the
          Sensors API.
    """
    @override
    def __init__(self, api_key: Optional[None] = None) -> None:
        super().__init__(api_key)
        self.all_contacts = self.get_all_contacts()


    def get_all_contacts(self) -> dict[str, Any]:
        """Get information from API about all contacts.

        Raises:
            Exception: If the request fails, raises an exception with the status code.
        """
        response = requests.get(
            f"{self.base_url}/contacts",
            headers = self.headers,
        )
        if response.status_code != 200:
            msg = f"Failed to get contacts. Status code: {response.status_code}"
            raise Exception(msg)
        return response.json()


    def get_contact_by_id(self, contact_id: Union[str, int]) -> dict[str, Any]:
        """Get a contact by the contact ID.

        Args:
            contact_id: ID number of the contact to retrieve information of.

        Returns:
            Dictionary with all information about the contact.

        Raises:
            Exception: If the request fails, raises an exception with the status code.
        """
        response = requests.get(
            f"{self.base_url}/contacts/{contact_id}",
            headers = self.headers,
        )
        if response.status_code != 200:
            msg = f"Failed to get contacts. Status code: {response.status_code}"
            raise Exception(msg)
        return response.json()


    def get_contact_by_name(self, contact_name: str) -> list[dict[str, Any]]:
        """Get a contact by contact's name.

        If multiple contacts are found with the same name, all are returned.

        Args:
            contact_name: First and last name of the contact.

        Returns:
            List of dictionaries with information of contact(s) matching name.
        """
        matching_contacts = []
        contact_first_name = contact_name.split(" ")[0].strip()
        contact_last_name = contact_name.split(" ")[-1].strip()
        for contact in self.all_contacts["data"]:
            if (contact["attributes"]["given_name"].strip() == contact_first_name
                and contact["attributes"]["family_name"].strip() == contact_last_name):
                matching_contacts.append(contact)
        return matching_contacts

        

    def get_contact_by_orcid(self, contact_orcid: str) -> Optional[dict[str, Any]]:
        """Get a contact by contact's ORCID

        Args:
            contact_orcid: ORCID of contact to get, in form 1234-5678-9012-3456

        Returns:
            Dictionary of contact with ORCID.
        """
        for contact in self.all_contacts["data"]:
            if (contact["attributes"]["orcid"] is not None 
                and contact["attributes"]["orcid"].strip() == contact_orcid.strip()):
                return contact
        return None
        

    def get_contact_by_email(self, contact_email: str) -> Optional[dict[str, Any]]:
        """Get a contact by contact's email address.

        Args:
            contact_orcid: email of contact to get.

        Returns:
            Dictionary of contact with email address.
        """
        for contact in self.all_contacts["data"]:
            if contact["attributes"]["email"].strip() == contact_email.strip():
                return contact
        return None

