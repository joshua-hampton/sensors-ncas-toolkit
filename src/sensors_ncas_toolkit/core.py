"""Core API class for requests to API

This module contains the CoreApi class which is the parent class for different
API requests. It includes setting the API key used in some requests.
"""

import os
from typing import Optional

class CoreApi:
    """Initialise for requests to API

    Parent class for different API requests. Includes setting API key used in some
    requests.

    Attributes:
        api_key: API key for requests
    """
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialise class with API key if available

        API key can either be provided as an argument or read from an environment
        variable called SENSORS_API_KEY.

        Args:
            api_key: API key for requests
        """
        self.api_key = api_key or os.getenv("SENSORS_API_KEY")
        self.base_url = "https://pid-sms-tst.bodc.uk/backend/api/v1"
        self.headers = {
            "accept": "application/vnd.api+json",
            "X-APIKEY": self.api_key,
            "Content-Type": "application/vnd.api+json"
        }

    def add_api_key(self, api_key: str) -> None:
        """Add API key to class

        Add API key to class if it was not provided during initialisation.

        Args:
            api_key: API key for requests
        """
        self.api_key = api_key


