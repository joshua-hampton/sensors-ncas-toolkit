"""Handle requests about sites from the Sensors API

This module contains the Sites class, which is used to handle requests to the Sensors
API, including getting site data, updating sites, and adding new sites.
"""

import json
import re
import requests
from .core import CoreApi
from .constants import SITE_ATTRIBUTES

from typing import Any, Optional, override, Union


class Sites(CoreApi):
    """Manage requests about sites

    Class that deals with requests to the Sensors API about sites.

    Attributes:
        base_url: The base url of the Sensors API
        headers: The headers of the request
        api_key: The api key to authenticate the request
        all_site_data: The json object containing all site information
    """
    @override
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.all_site_data = None


    def get_sites(self) -> None:
        """Get all site information

        Gets all information for all sites from the Sensors API, and saves response as
        a json object.

        Raises:
            Exception: If the request fails, raises an exception with the status code
        """
        response = requests.get(f"{self.base_url}/sites", headers=self.headers)
        if response.status_code != 200:
            msg = f"Failed to get sites. Status code: {response.status_code}"
            raise Exception(msg)
        self.all_site_data = response.json()
     

    def get_site_by_id(self, site_id: Union[str, int]) -> dict[str, Any]:
        """Get site information by site id

        Gets information for a specific site by its site id from the Sensors API.

        Args:
            site_id: The id of the site to get information about

        Returns:
            A dictionary containing the information about the site

        Raises:
            Exception: If the request fails, raises an exception with the status code
        """
        response = requests.get(
            f"{self.base_url}/sites/{site_id}",
            headers=self.headers,
        )
        if response.status_code != 200:
            msg = f"Failed to get site. Status code: {response.status_code}"
            raise Exception(msg)
        return response.json()["data"]


    def get_site_by_name(self, site_name: str) -> dict[str, Any]:
        """Get site information by site name

        Searches through all sites to find a site with the specified label.

        Args:
            site_name: The label of the site to get information about

        Returns:
            A dictionary containing the information about the site

        Raises:
            ValueError: If no site found with name, raises an exception
        """
        if self.all_site_data is None:
            self.get_sites()
        for site in self.all_site_data["data"]:
            if site["attributes"]["label"] == site_name:
                return site
        msg = f"Failed to find site with name: {site_name}"
        raise ValueError(msg)


    def get_sites_by_name(self, site_name_pattern: str) -> list[dict[str, Any]]:
        """Get information on sites matching a regex pattern

        Searches through all sites to find sites with label that match the specified
        pattern.

        Args:
            site_name_pattern: Regex pattern to match site names

        Returns:
            A list of dictionaries containing the information about the sites

        Raises:
            ValueError: If no sites found matching pattern, raises an exception
        """
        if self.all_site_data is None:
            self.get_sites()
        sites = []
        for site in self.all_site_data["data"]:
            if re.match(site_name_pattern, site["attributes"]["label"]):
                sites.append(site)
        if not sites:
            msg = f"Failed to find site matching pattern: {site_name_pattern}"
            raise ValueError(msg)
        return sites


    def get_site_configurations(
        self,
        site_id: Union[str, int, None] = None,
        site_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get configurations associated with a site

        Return all configurations associated with a site, defined by either its ID or
        its name. Only one of `site_id` and `site_name` needed.

        Args:
            site_id: ID of the site to get configurations for
            site_name: Name of site to get configurations for

        Returns:
            A dictionary of all configurations for the site

        Raises:
            Exception: If request fails, raise an exception with the status code.
        """
        if site_id is not None and site_name is not None:
            site = self.get_site_by_id(site_id)
            if site["attributes"]["label"] != site_name:
                raise ValueError("Site id and name do not match")

        if site_id is None and site_name is None:
            raise ValueError("Must provide either site_id or site_name")

        if site_name is not None:
            site_id = self.get_site_by_name(site_name)["id"]

        response = requests.get(
            f"{self.base_url}/sites/{site_id}/configurations",
            headers = self.headers
        )
        if response.status_code != 200:
            msg = f"Failed to get configuration. Status code: {response.status_code}"
            raise Exception(msg)
        return response.json()


    def update_site_by_id(
            self,
            site_id: Union[str, int],
            attributes: dict[str, Union[str, list[str]]],
    ) -> None:
        """Update attributes of a site

        Updates attributes for a given site id.

        Args:
            site_id: The id of the site to update attributes for
            attributes: Dictionary of attributes and values to update

        Raises:
            ValueError: If invalid attribute names are given, raises an error
            Exception: If the request fails, raise an exception with the status code
        """
        invalid_attrs = []
        for attr in attributes.keys():
            if attr not in SITE_ATTRIBUTES:
                invalid_attrs.append(attr)
        if len(invalid_attrs) > 0:
            msg = f"Invalid attributes given for updating site: {invalid_attrs}"
            raise ValueError(msg)

        response = requests.patch(
            f"{self.base_url}/sites/{site_id}",
            headers = self.headers,
            data = json.dumps({
                "data": {
                    "id": f"{site_id}",
                    "type": "site",
                    "attributes": attributes,
                }
            })
        )
        if response.status_code != 200:
            msg = (
                f"Failed to update site {site_id}. "
                f"Status code: {response.status_code}"
            )
            raise Exception(msg)


    def update_site_by_name(
            self,
            site_name: str,
            attributes: dict[str, Union[str, list[str]]],
    ) -> None:
        """Update attributes of a site

        Update the attributes of a site given by its name by finding the sites id
        and calling `update_site_by_id()`.

        Args:
            site_name: The name of the site to update
            attributes: Dictionary of attributes and values to update 
        """
        site_id = self.get_site_by_name(site_name)["id"]
        self.update_site_by_id(site_id, attributes)



