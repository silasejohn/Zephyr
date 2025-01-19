from __init__ import update_sys_path
update_sys_path()

from scripts.api.riot_api_client import Account_V1
from models.AccountDTO import AccountDTO

# import sys
# # Sample Usage of Accessing AccountDTO from API given Riot ID
# response_code, json_data = Account_V1.get_account_by_riot_id("dont ever stop", "NA1")

# print(f"Response Code: {response_code}")
# print(f"Response JSON: {json_data}")

# # store the response in AccountDTO object
# account_dto_ex_1 = AccountDTO.from_json(json_data)

# # print the AccountDTO object
# print(account_dto_ex_1)

""""""

# # Sample Usage of Accessing AccountDTO from API given Riot ID
# response_code, reponse_json = Account_V1.get_account_by_puuid("g9pA1AhAi5KBJC5J_EM0cxBIbFLXEsfoJjfzz4zK0UmY-oOG69eQcvmI6U68N1xdwSq0cR2JPi7WQw")

# print(f"Response Code: {response_code}")
# print(f"Response JSON: {json_data}")

# # store the response in AccountDTO object
# account_dto_ex_2 = AccountDTO.from_json(json_data)

# # print the AccountDTO object
# print(account_dto_ex_2)

""""""

# # Sample Usage of Accessing MatchIDs from API given PUUID
from scripts.api.riot_api_client import MATCH_V5
from scripts.utils.riot_api_helpers import get_epoch_timestamp, get_current_epoch_timestamp, save_json_to_file

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

""""""
import os, json

# access all json files in /data/custom_examples, and their 'metadata' key and the 'participants' key within it and print 
for file in os.listdir("data/custom_examples"):
    if file.endswith(".json"):
        with open(f"data/custom_examples/{file}") as f:
            data = json.load(f)
            print(f"File: {file}")
            print(f"Metadata: {data['metadata']}")
            participants_list = data['metadata']['participants']
            for participant_puuid in participants_list:
                response_code, reponse_json = Account_V1.get_account_by_puuid(participant_puuid)
                account_dto_ex_2 = AccountDTO.from_json(reponse_json)
                print(f"Participant: {account_dto_ex_2.gameName}#{account_dto_ex_2.tagLine}")
            print("\n")







