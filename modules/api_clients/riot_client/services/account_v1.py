###############
### IMPORTS ###
###############

# system imports
import requests, time
from urllib.parse import urlencode

# local imports
from __init__ import update_sys_path 
update_sys_path()
from config.config import get_riot_api_config

# access API Environment Variables
RIOT_API_KEY = get_riot_api_config("RIOT_API_KEY")
DEFAULT_REGION_CODE = get_riot_api_config("DEFAULT_REGION_CODE")
MAX_RETRY_ATTEMPTS = int(get_riot_api_config("MAX_RETRY_ATTEMPTS"))
RETRY_DELAY = int(get_riot_api_config("RETRY_DELAY"))

##################
### ACCOUNT_V1 ###
##################
class ACCOUNT_V1:

    @staticmethod   
    def get_account_by_riot_id(game_name: str = None, tag_line: str = None, region: str = DEFAULT_REGION_CODE) -> dict:
        """
        Wrapper for ACCOUNT_V1 API Portal
        [info] access player puuid by their riot id 
        [param] riot id & tag
        [return] AccountDTO or None (if issue)
        """
        if not game_name:
            game_name = input("Enter Riot ID (no tag): ")

        if not tag_line:
            tag_line = input("Enter Tag Line: ")

        params = {
            'api_key': RIOT_API_KEY
        }

        api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

        retries = 0
        while retries < MAX_RETRY_ATTEMPTS:
            try:
                response = requests.get(api_url, params=urlencode(params))  # make the request w/ API 
                response.raise_for_status()                                 # check for any errors
                return response.status_code, response.json()                # return the json response
            except requests.exceptions.RequestException as e:
                if 500 <= response.status_code < 600:                        # checking for 5XX error
                    print(f"[Server Error - {response.status_code}] retrying... ({retries + 1}/{MAX_RETRY_ATTEMPTS})")
                    retries += 1
                    time.sleep(RETRY_DELAY)
                elif response.status_code == 429: # rate limit exceeded
                    time.sleep(RETRY_DELAY * 3)
                else:
                    print(f"[get_account_by_riot_id] ({response.status_code})Issue fetching AccountDTO from API: {e}")
                    return None
        print(f"Failed to fetch AccountDTO after {MAX_RETRY_ATTEMPTS} attempts")
        return None

    @staticmethod   
    def get_account_by_puuid(puuid: str, region: str = DEFAULT_REGION_CODE) -> dict:
        """
        Wrapper for ACCOUNT_V1 API Portal
        [info] access player IGN & Tag by their riot id 
        [param] puuid
        [return] AccountDTO or None (if issue)
        """
        params = {
            'api_key': RIOT_API_KEY
        }

        api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"

        retries = 0
        while retries < MAX_RETRY_ATTEMPTS:
            try:
                response = requests.get(api_url, params=urlencode(params))  # make the request w/ API 
                response.raise_for_status()                                 # check for any errors
                return response.status_code, response.json()                # return the json response
            except requests.exceptions.RequestException as e:
                if 500 <= response.status_code < 600:                        # checking for 5XX error
                    print(f"[Server Error - {response.status_code}] retrying... ({retries + 1}/{MAX_RETRY_ATTEMPTS})")
                    retries += 1
                    time.sleep(RETRY_DELAY)
                elif response.status_code == 429: # rate limit exceeded
                    time.sleep(RETRY_DELAY * 3)
                else:
                    print(f"[get_account_by_puuid] ({response.status_code})Issue fetching AccountDTO from API: {e}")
                    return None
        print(f"Failed to fetch AccountDTO after {MAX_RETRY_ATTEMPTS} attempts")
        return None