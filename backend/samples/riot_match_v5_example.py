###############
### IMPORTS ###
###############

# global imports
import sys, os

# local imports
from __init__ import update_sys_path
update_sys_path()
from modules.api_clients.riot_client.services.match_v5 import MATCH_V5
from modules.utils.file_utils import save_json_to_file, load_json_from_file

############
### EX 1 ###
############

# # Sample Usage of Accessing MatchIDs from API given PUUID
# match_list = [] # list to store match ids
# example_puuid = "g9pA1AhAi5KBJC5J_EM0cxBIbFLXEsfoJjfzz4zK0UmY-oOG69eQcvmI6U68N1xdwSq0cR2JPi7WQw" # dont ever stop#NA1
# example_queue_id = 0 # 0 is for custom games
# response_code, response_json = MATCH_V5.get_match_ids_by_puuid(example_puuid, queue=0)
# match_list.extend(response_json) # add the match ids to the list
# print(f"Response Code: {response_code}")
# print(f"Response JSON: {response_json}")

""""""

############
### EX 2 ###
############

# # Sample Usage of Accessing MatchDTO from API given MatchID

# load data_file, pull match ids
data_file = "../data/official_tourney_games/GCS_tourney_match_overview_week2.json"
data = load_json_from_file(data_file)
data_keys = data.keys()
for key in data_keys:
    match_info = data[key]["match_info"]
    match_keys = match_info.keys()

    team_ids = data[key]["team_ids"]
    winning_team_id = data[key]["match_info"]["winning_team_id"]

    for match_key in match_keys:

        # ensure that we are pulling the correct match data
        if not match_key.startswith("match_"):
            continue

        # get match_id
        match_id = match_info[match_key]["match_id"]
       
        # skip if match_id is empty
        if match_id == "" or match_id == "%":
            continue

        # pre-append NA1_ to match_id
        match_id = f"NA1_{match_id}"

        # construct output file name
        output_file_name = f"../data/official_tourney_games/{match_id}_{key}_{match_key}.json"

        # if output file already exists, then move on to the next match
        if os.path.basename(output_file_name) in os.listdir("../data/official_tourney_games"):
            print(f"File already exists: {output_file_name}")
            continue
        
        # get match data by match_id
        response_code, response_json = MATCH_V5.get_match_by_id(match_id)
        print(f"Response Code: {response_code}")

        # add some additional data to response_json MatchDTO
        response_json["team_ids"] = team_ids
        response_json["winning_team_id"] = winning_team_id

        save_json_to_file(response_json, output_file_name)
    

""""""

############
### EX 3 ###
############

# Feed a custom list of match ids to the API & generate MatchDTO JSON files for each match

# match_list = [
#     "NA1_5209540316",
#     "NA1_5209504484",
#     "NA1_5153185984",
#     "NA1_5153126506",
#     "NA1_5153092040",
#     "NA1_5148623957",
#     "NA1_5148558129"
# ]

# for game_id in match_list:
#     response_code, response_json = MATCH_V5.get_match_by_id(game_id)
#     save_json_to_file(response_json, f"../data/custom_examples/test_match_data_{game_id}.json") # ../data/test/
#     print(f"Response Code: {response_code}")

# # Good Games: "gameType": "CUSTOM_GAME"
