###############
### IMPORTS ###
###############

# system imports
import requests
from urllib.parse import urlencode

# local imports
from __init__ import update_sys_path 
update_sys_path()
from config.config import get_riot_api_config
from modules.utils.time_utils import get_current_epoch_timestamp, get_epoch_timestamp

# access API Environment Variables
RIOT_API_KEY = get_riot_api_config("RIOT_API_KEY")
DEFAULT_REGION_CODE = get_riot_api_config("DEFAULT_REGION_CODE")

################
### MATCH_V5 ###
################
class MATCH_V5:
    
    @staticmethod
    def get_match_ids_by_puuid(puuid: str, startTime: int = None, endTime: int = None, queue: int = None, type: str = None, start: int = None, count: int = None, region: str = DEFAULT_REGION_CODE) -> list:
        """
        Wrapper for MATCH_V5 API Portal
        [info] access match ids by player puuid
        [param] puuid (string)
        [param] startTime (long) - epoch timestamp in seconds ... starts June 16th, 2021
        [param] endTime (long) - epoch timestamp in seconds 
        [param] queue (int) - sort by queue ID (queues.json)
        [param] type (string) - sort by match type
        [param] start (int) - start index (default 0)
        [param] count (int) - number of matches to return (default 20, 0 - 100)
        [return] List[GameID]... GameID (str) or None (if issue)
        """
        if not startTime:
            startTime = get_epoch_timestamp(6, 17, 2021)
        
        if not endTime:
            endTime = get_current_epoch_timestamp()

        if not count:
            count = 20

        if not start:
            start = 0

        if not queue:
            queue = 420 # ranked solo / duo

        # if not type:
        #     type = "RANKED_SOLO_5x5"

        params = {
            'api_key': RIOT_API_KEY,
            'puuid': puuid,
            'startTime': startTime,
            'endTime': endTime,
            'queue': queue,
            # 'type': type,
            'start': start,
            'count': count
        }
        # PUUID: g9pA1AhAi5KBJC5J_EM0cxBIbFLXEsfoJjfzz4zK0UmY-oOG69eQcvmI6U68N1xdwSq0cR2JPi7WQw 

        """
        {
            "queueId": 700,
            "map": "Summoner's Rift",
            "description": "Summoner's Rift Clash games",
            "notes": null
        }
        {
            "queueId": 490,
            "map": "Summoner's Rift",
            "description": "Normal (Quickplay)",
            "notes": null
        }
        {
            "queueId": 440,
            "map": "Summoner's Rift",
            "description": "5v5 Ranked Flex games",
            "notes": null
        }
        {
            "queueId": 430,
            "map": "Summoner's Rift",
            "description": "5v5 Blind Pick games",
            "notes": null
        }
        {
            "queueId": 420,
            "map": "Summoner's Rift",
            "description": "5v5 Ranked Solo games",
            "notes": null
        }
        {
            "queueId": 400,
            "map": "Summoner's Rift",
            "description": "5v5 Draft Pick games",
            "notes": null
        }
        {
            "queueId": 325,
            "map": "Summoner's Rift",
            "description": "All Random games",
            "notes": null
        }
        {
            "queueId": 0,
            "map": "Custom games",
            "description": null,
            "notes": null
        }

        SUMMONERS RIFT RANKED TYPES
        Unranked
            RANKED_SOLO_5x5
            RANKED_TEAM_5x5
        Ranked Solo/Duo
            RANKED_SOLO_5x5
        Ranked Team 5x5
            RANKED_TEAM_5x5

        """

        api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"

        try:
            response = requests.get(api_url, params=urlencode(params))  # make the request w/ API 
            response.raise_for_status()                                 # check for any errors
            return response.status_code, response.json()                # return the json response
        except requests.exceptions.RequestException as e:
            print(f"Issue fetching MatchDTO from API: {e}")
            return None
        
    @staticmethod
    def get_match_by_id(match_id: str, region: str = DEFAULT_REGION_CODE) -> dict:
        """
        Wrapper for MATCH_V5 API Portal
        [info] access match by match id
        [param] match id (string)
        [return] MatchDTO or None (if issue)
        """
        params = {
            'api_key': RIOT_API_KEY
        }

        api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"

        try:
            response = requests.get(api_url, params=urlencode(params))  # make the request w/ API 
            response.raise_for_status()                                 # check for any errors
            return response.status_code, response.json()                # return the json response
        except requests.exceptions.RequestException as e:
            print(f"Issue fetching MatchDTO from API: {e}")
            return None
        

# (1) Getting a given player’s puuid by their player name.
# (2) Using their puuid to get the ids of the last 20 matches they have played.
# (3) Get the match information associated with each match id and tally up the wins and losses
# (4) Calculate and return their win percentage

"""
dont ever stop custom games
[
    "NA1_5209540316",
    "NA1_5209504484",
    "NA1_5153185984",
    "NA1_5153126506",
    "NA1_5153092040",
    "NA1_5148623957",
    "NA1_5148558129"
]
"""