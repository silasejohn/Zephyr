from __init__ import update_sys_path 
update_sys_path(False)

import requests, json
from urllib.parse import urlencode
from config.config import get_riot_api_config
from scripts.utils.riot_api_helpers import get_current_epoch_timestamp, get_epoch_timestamp

# Access API Environment Variables
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
            return response.status_code, response.json()                # return the json response
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
            return response.status_code, response.json()                # return the json response
        except requests.exceptions.RequestException as e:
            print(f"Issue fetching AccountDTO from API: {e}")
            return None
        
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
            start_time = get_epoch_timestamp(1, 1, 2025)
        
        if not endTime:
            end_time = get_current_epoch_timestamp()

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
            # 'queue': queue,
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
[
    "NA1_5209966712",
    "NA1_5209788000",
    "NA1_5209540316",
    "NA1_5209504484",
    "NA1_5209418196",
    "NA1_5209215506",
    "NA1_5209169559",
    "NA1_5209137876",
    "NA1_5209129000",
    "NA1_5208913973",
    "NA1_5208706529",
    "NA1_5208695993",
    "NA1_5208549056",
    "NA1_5208508833",
    "NA1_5208497107",
    "NA1_5208043330",
    "NA1_5208028463",
    "NA1_5206495322",
    "NA1_5206474272",
    "NA1_5206456447",
    "NA1_5206097513",
    "NA1_5206077800",
    "NA1_5206048432",
    "NA1_5206028293",
    "NA1_5206001117",
    "NA1_5204913968",
    "NA1_5204871046",
    "NA1_5204816014",
    "NA1_5204776459",
    "NA1_5204432300",
    "NA1_5204097578",
    "NA1_5204078447",
    "NA1_5202583552",
    "NA1_5202559519",
    "NA1_5202545234",
    "NA1_5202351780",
    "NA1_5202309446",
    "NA1_5202272854",
    "NA1_5201722161",
    "NA1_5201692302",
    "NA1_5201663883",
    "NA1_5201597831",
    "NA1_5201567919",
    "NA1_5201481870",
    "NA1_5201362012",
    "NA1_5201340734",
    "NA1_5201321555",
    "NA1_5201306838",
    "NA1_5201038127",
    "NA1_5200916554",
    "NA1_5200880236",
    "NA1_5200848401",
    "NA1_5200174343",
    "NA1_5200148962",
    "NA1_5199121191",
    "NA1_5199095519",
    "NA1_5198758889",
    "NA1_5198740888",
    "NA1_5198431597",
    "NA1_5198392290",
    "NA1_5198372602",
    "NA1_5197954956",
    "NA1_5197927918",
    "NA1_5197899642",
    "NA1_5197872896",
    "NA1_5197834187",
    "NA1_5197745911",
    "NA1_5197716570",
    "NA1_5197690561",
    "NA1_5197666247",
    "NA1_5197227953",
    "NA1_5197217837",
    "NA1_5197197011",
    "NA1_5195523219",
    "NA1_5195465739",
    "NA1_5194863041",
    "NA1_5194594419",
    "NA1_5189861262",
    "NA1_5189822895",
    "NA1_5189708921",
    "NA1_5189692291",
    "NA1_5189686384",
    "NA1_5187657845",
    "NA1_5187644900",
    "NA1_5187626514",
    "NA1_5187471130",
    "NA1_5187150299",
    "NA1_5187130605",
    "NA1_5187110769",
    "NA1_5187011947",
    "NA1_5186792486",
    "NA1_5186775798",
    "NA1_5186755187",
    "NA1_5186738427",
    "NA1_5186719723",
    "NA1_5186644413",
    "NA1_5186603990",
    "NA1_5186562428",
    "NA1_5186542884",
    "NA1_5186489068"
]
"""