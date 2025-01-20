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
    def __init__(self, url, params, callback, max_retries=5):
        self.url = url
        self.params = params
        self.callback = callback
        self.max_retries = max_retries
        self.last_request_time = None
        # some sort of delay before adding back to queue?

    def make_request(self):
        try:
            response = requests.get(self.url, params=urlencode(self.params))
            return response
            # response.status_code, response.json()
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
