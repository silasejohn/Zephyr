# data_models/api_object.py

###############
### IMPORTS ###
###############

# system imports
import requests
from urllib.parse import urlencode
import logging

# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class APIObject:
    """
    [info] Represents an API request object with retry logic and rate limiting support
    """
    def __init__(self, url: str, params: dict, callback, max_retries: int = 5) -> None:
        """
        [info] Initialize API object with request parameters
        [param] url: API endpoint URL
        [param] params: Dictionary of query parameters
        [param] callback: Callback function to handle response
        [param] max_retries: Maximum number of retry attempts (default: 5)
        [return] None
        """
        self.url = url
        self.params = params
        self.callback = callback
        self.max_retries = max_retries
        self.last_request_time = None
        # some sort of delay before adding back to queue?

    def make_request(self):
        """
        [info] Execute the API request with error handling
        [return] Response object or None if request fails
        """
        try:
            response = requests.get(self.url, params=urlencode(self.params))
            return response
            # response.status_code, response.json()
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
