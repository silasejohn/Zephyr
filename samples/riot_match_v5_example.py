###############
### IMPORTS ###
###############

# local imports
from __init__ import update_sys_path
update_sys_path(True)
from modules.api_clients.riot_client.services.match_v5 import MATCH_V5
from modules.utils.time_utils import get_epoch_timestamp, get_current_epoch_timestamp
from modules.utils.file_utils import save_json_to_file

# # Sample Usage of Accessing MatchIDs from API given PUUID

# # get the epoch timestamp for the last 7 days
# match_list = []
# # start_time = get_epoch_timestamp(1, 1, 2025)
# # end_time = get_current_epoch_timestamp()

# response_code, response_json = MATCH_V5.get_match_ids_by_puuid("g9pA1AhAi5KBJC5J_EM0cxBIbFLXEsfoJjfzz4zK0UmY-oOG69eQcvmI6U68N1xdwSq0cR2JPi7WQw", queue=0)
# match_list.extend(response_json) # add the match ids to the list
# print(f"Response Code: {response_code}")
# print(f"Response JSON: {response_json}")

# # Sample Usage of Accessing MatchDTO from API given MatchID
# from scripts.api.riot_api_client import MATCH_V5
# # from models.MatchDTO import MatchDTO

match_list = [
    "NA1_5209540316",
    "NA1_5209504484",
    "NA1_5153185984",
    "NA1_5153126506",
    "NA1_5153092040",
    "NA1_5148623957",
    "NA1_5148558129"
]

for game_id in match_list:
    response_code, response_json = MATCH_V5.get_match_by_id(game_id)
    save_json_to_file(response_json, f"data/custom_examples/test_match_data_{game_id}.json") # ../data/test/
    print(f"Response Code: {response_code}")

# # Good Games: "gameType": "CUSTOM_GAME"
