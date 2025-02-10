"""Handle requests about devices from the Sensors API

This module contains the Devices class, which is used to handle requests to the Sensors
API, including getting device data, updating devices, and adding new devices.
"""

import json
import requests
import re
from .core import CoreApi
from .constants import (
    DEVICE_ATTRIBUTES, 
    MIN_PRIVATE_DEVICE_ATTRIBUTES, 
    MIN_INTERNAL_DEVICE_ATTRIBUTES,
    MIN_PUBLIC_DEVICE_ATTRIBUTES,
)

from typing import Any, Optional, override, Union


class Devices(CoreApi):
    """Manage requests about devices

    Class that deals with requests to the Sensors API about devices.

    Attributes:
        base_url: The base url of the Sensors API
        headers: The headers of the request
        api_key: The api key to authenticate the request
        all_device_data: The json object containing all device information
    """
    @override
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.all_device_data = None


    def _check_device_visibility(self, input_dict: dict[str, Any]) -> str:
        """Check if device is private, internal or public

        Given a dictionary with keys "is_public", "is_internal", and "is_private",
        returns which is true and errors if none or multiple are true.

        Args:
            input_dict: dictionary that includes, but is not limited to, keys
              "is_public", "is_internal", and "is_private"

        Returns:
            The key which has a true value.

        Raises:
            ValueError: If one of the keys has an invalid value, or if none or multiple
              keys have a true value, raises error.
        """
        true_keys = []
        for key in ["is_public", "is_internal", "is_private"]:
            value = input_dict[key]
            if isinstance(value, str):
                value = value.lower()
                if value in ["true", "1"]:
                    value = True
                elif value in ["false", "0"]:
                    value = False
                else:
                    msg = f"Invalid boolean string value for {key}: {input_dict[key]}."
                    raise ValueError(msg)
            elif not isinstance(value, bool):
                msg = f"Value for {key} must be boolean or a boolean string"
                raise TypeError(msg)

            if value:
                true_keys.append(key)

        if len(true_keys) > 1:
            msg = f"Multiple visibilities defined as true: {true_keys}."
            raise ValueError(msg)
        elif len(true_keys) == 0:
            msg = f"No visibilities defined as true."
            raise ValueError(msg)
        else:
            return true_keys[0]


    def get_devices(self) -> None:
        """Get all device information

        Gets all information for all devices from the Sensors API, and saves response
        as a json object.

        Raises:
            Exception: If the request fails, raises an exception with the status code
        """
        response = requests.get(f"{self.base_url}/devices", headers=self.headers)
        if response.status_code != 200:
            msg = f"Failed to get devices. Status code: {response.status_code}"
            raise Exception(msg)
        self.all_device_data = response.json()
     

    def get_device_by_id(self, device_id: Union[str, int]) -> dict[str, Any]:
        """Get device information by device id

        Gets information for a specific device by its device id from the Sensors API.

        Args:
            device_id: The id of the device to get information about

        Returns:
            A dictionary containing the information about the device

        Raises:
            Exception: If the request fails, raises an exception with the status code
        """
        response = requests.get(
            f"{self.base_url}/devices/{device_id}",
            headers=self.headers,
        )
        if response.status_code != 200:
            msg = f"Failed to get device. Status code: {response.status_code}"
            raise Exception(msg)
        return response.json()["data"]


    def get_device_by_name(self, device_name: str) -> dict[str, Any]:
        """Get device information by device name

        Searches through all devices to find a device with the specified short name.

        Args:
            device_name: The short name of the device to get information about

        Returns:
            A dictionary containing the information about the device

        Raises:
            ValueError: If no device found with name, raises an exception
        """
        if self.all_device_data is None:
            self.get_devices()
        for device in self.all_device_data["data"]:
            if device["attributes"]["short_name"] == device_name:
                return device
        msg = f"Failed to find device with name: {device_name}"
        raise ValueError(msg)


    def get_devices_by_name(self, device_name_pattern: str) -> list[dict[str, Any]]:
        """Get information on devices matching a regex pattern

        Searches through all devices to find a device with the specified short name.

        Args:
            device_name_pattern: Regex pattern to match device names

        Returns:
            A list of dictionaries containing the information about the devices

        Raises:
            ValueError: If no devices found matching pattern, raises an exception
        """
        if self.all_device_data is None:
            self.get_devices()
        devices = []
        for device in self.all_device_data["data"]:
            if re.match(device_name_pattern, device["attributes"]["short_name"]):
                devices.append(device)
        if not devices:
            msg = f"Failed to find device with name: {device_name_pattern}"
            raise ValueError(msg)
        return devices


    def get_device_properties(
            self,
            device_id: Union[str, int, None] = None,
            device_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get device properties by device id or name

        Gets the properties of a device by its id or name. If both are provided and
        they don't match, a ValueError is raised.

        Args:
            device_id: The id of the device to get properties for
            device_name: The short name of the device to get properties for

        Returns:
            A dictionary containing the properties of the device

        Raises:
            ValueError: If id and name do not match or neither are given, raises an 
                exception
            Exception: If the request fails, raises an exception with the status code
        """
        if device_id is not None and device_name is not None:
            device = self.get_device_by_id(device_id)
            if device["attributes"]["short_name"] != device_name:
                raise ValueError("Device id and name do not match")

        if device_id is None and device_name is None:
            raise ValueError("Must provide either device_id or device_name")

        if device_name is not None:
            device_id = self.get_device_by_name(device_name)["id"]

        response = requests.get(
            f"{self.base_url}/device-properties?filter[device_id]={device_id}",
            headers = self.headers,
        )
        if response.status_code != 200:
            msg = (
                "Failed to get device properties. "
                f"Status code: {response.status_code}"
            )
            raise Exception(msg)
        return response.json()


    def get_devices_by_property(
            self,
            property: str,
            return_id: bool = False
    ) -> list[str]:
        """Get all devices with a given property.

        Returns a list of all devices with a given property. Can return either device
        names or device id. 

        Args:
            property: property name to search for
            return_id: return device ids instead of device names. Default False.

        Returns:
            A list of all devices, by name or by id, containing the given property.

        Raises:
            Exception: If the request fails, raise an exception with the status code
        """
        response = requests.get(
            f"{self.base_url}/device-properties?filter[property_name]={property}",
            headers = self.headers,
        )
        if response.status_code != 200:
            msg = (
                "Failed to get device properties. "
                f"Status code: {response.status_code}"
            )
            raise Exception(msg)

        devices = []
        for each in response.json()["data"]:
            d_id = each["relationships"]["device"]["data"]["id"]
            if return_id:
                devices.append(d_id)
            else:
                d_name = self.get_device_by_id(d_id)["attributes"]["short_name"]
                devices.append(d_name)

        return devices


    def update_device_by_id(
            self,
            device_id: Union[str, int],
            attributes: dict[str, Union[str, list[str], bool]],
    ) -> None:
        """Update attributes of a device

        Updates attributes for a given device id.

        Args:
            device_id: The id of the device to update attributes for
            attributes: Dictionary of attributes and values to update

        Raises:
            ValueError: If invalid attribute names are given, raises an error
            Exception: If the request fails, raise an exception with the status code
        """
        invalid_attrs = []
        for attr in attributes.keys():
            if attr not in DEVICE_ATTRIBUTES:
                invalid_attrs.append(attr)
        if len(invalid_attrs) > 0:
            msg = f"Invalid attributes given for updating device: {invalid_attrs}"
            raise ValueError(msg)

        response = requests.patch(
            f"{self.base_url}/devices/{device_id}",
            headers = self.headers,
            data = json.dumps({
                "data": {
                    "id": f"{device_id}",
                    "type": "device",
                    "attributes": attributes,
                }
            }),
        )
        if response.status_code != 200:
            msg = (
                f"Failed to update device {device_id}. "
                f"Status code: {response.status_code}"
            )
            raise Exception(msg)


    def update_device_by_name(
            self,
            device_name: str,
            attributes: dict[str, Union[str, list[str], bool]],
    ) -> None:
        """Update attributes of a device

        Update the attributes of a device given by its name by finding the devices id
        and calling `update_device_by_id()`.

        Args:
            device_name: The name of the device to update
            attributes: Dictionary of attributes and values to update 
        """
        device_id = self.get_device_by_name(device_name)["id"]
        self.update_device_by_id(device_id, attributes)


    def add_device(
            self,
            attributes: dict[str, Union[str, list[str], bool]],
    ) -> None:
        """Add new device

        Adds a new device to the Sensors database.

        Args:
            attributes: Dictionary of attributes and values for new device. Attributes
              checked against minimum requirements for device and all allowed
              attributes.
        
        Raises:
            ValueError: If invalid attribute names are given, or required attributes
              are missing, raises an error
            Exception: If the request fails, raise an exception with the status code
        """
        for key in ["is_private", "is_internal", "is_public"]:
            if key not in attributes:
                attributes[key] = False

        vis = self._check_device_visibility(attributes)
        if vis == "is_private":
            min_reqs = MIN_PRIVATE_DEVICE_ATTRIBUTES
        elif vis == "is_internal":
            min_reqs = MIN_INTERNAL_DEVICE_ATTRIBUTES
        else:
            min_reqs = MIN_PUBLIC_DEVICE_ATTRIBUTES

        given_min_reqs = []
        for attr in attributes.keys():
            if attr not in DEVICE_ATTRIBUTES:
                msg = f"Invalid attribute given: {attr}"
                raise ValueError(msg)
            if attr in min_reqs:
                given_min_reqs.append(attr)
        if len(min_reqs) != len(given_min_reqs):
            missing = list(set(min_reqs) - set(given_min_reqs))
            msg = f"Missing required attributes: {missing}"
            raise ValueError(msg)

        response = requests.post(
            f"{self.base_url}/devices",
            headers = self.headers,
            data = json.dumps({
                "data": {
                    "type": "device",
                    "attributes": attributes,
                }
            }),
        )
        if response.status_code != 201:
            msg = f"Failed to add new device. Status code: {response.status_code}"
            raise Exception(msg)


