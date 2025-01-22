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
DEFAULT_REGION_CODE = get_riot_api_config("DEFAULT_REGION_CODE") # americas
DEFAULT_REGION_EXECUTION = get_riot_api_config("DEFAULT_REGION_EXECUTION") # NA1
MAX_RETRY_ATTEMPTS = int(get_riot_api_config("MAX_RETRY_ATTEMPTS"))
RETRY_DELAY = int(get_riot_api_config("RETRY_DELAY"))

###################
### SUMMONER_V4 ###
###################
class SUMMONER_V4:

    @staticmethod   
    def get_summoner_info_by_puuid(puuid: str = None, region: str = DEFAULT_REGION_EXECUTION) -> dict:
        """
        Wrapper for SUMMONER_V4 API Portal
        [info] access accountID, summonerID, summonerLevel by their puuid
        [param] puuid
        [return] SummonerDTO or None (if issue)
        """
        if not puuid:
            puuid = input("Enter player puuid: ")

        params = {
            'api_key': RIOT_API_KEY
        }

        api_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"

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
                    print(f"[get_summoner_info_by_puuid] ({response.status_code})Issue fetching SummonerDTO from API: {e}")
                    return None
        print(f"Failed to fetch SummonerDTO after {MAX_RETRY_ATTEMPTS} attempts")
        return None