from __init__ import update_sys_path 
update_sys_path(True)


import requests
from urllib.parse import urlencode
from config.config import get_riot_api_config

# Access the environment variables
RIOT_API_KEY = get_riot_api_config("RIOT_API_KEY")
DEFAULT_REGION_CODE = get_riot_api_config("DEFAULT_REGION_CODE")

# PUUID: g9pA1AhAi5KBJC5J_EM0cxBIbFLXEsfoJjfzz4zK0UmY-oOG69eQcvmI6U68N1xdwSq0cR2JPi7WQw 

##################
### ACCOUNT_V1 ###
##################
class Account_V1:
    
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

        try:
            response = requests.get(api_url, params=urlencode(params))  # make the request w/ API 
            response.raise_for_status()                                 # check for any errors
            return response.json()                                      # return the json response
        except requests.exceptions.RequestException as e:
            print(f"Issue fetching AccountDTO from API: {e}")
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

        try:
            response = requests.get(api_url, params=urlencode(params))  # make the request w/ API 
            response.raise_for_status()                                 # check for any errors
            return response.json()                                      # return the json response
        except requests.exceptions.RequestException as e:
            print(f"Issue fetching AccountDTO from API: {e}")
            return None

# (1) Getting a given player’s puuid by their player name.
# (2) Using their puuid to get the ids of the last 20 matches they have played.
# (3) Get the match information associated with each match id and tally up the wins and losses
# (4) Calculate and return their win percentage
