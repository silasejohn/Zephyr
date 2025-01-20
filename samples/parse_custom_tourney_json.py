###############
### IMPORTS ###
###############

# global imports
import os, json

# local imports
from __init__ import update_sys_path
update_sys_path(True)
from modules.api_clients.riot_client.services.account_v1 import ACCOUNT_V1
from models.account_dto import AccountDTO

############
### EX 1 ###
############

# access all json files in /data/custom_examples, and their 'metadata' key and the 'participants' key within it and print 
for file in os.listdir("data/custom_examples"):
    if file.endswith(".json"):
        with open(f"data/custom_examples/{file}") as f:
            data = json.load(f)
            print(f"File: {file}")
            print(f"Metadata: {data['metadata']}")
            participants_list = data['metadata']['participants']
            for participant_puuid in participants_list:
                response_code, reponse_json = ACCOUNT_V1.get_account_by_puuid(participant_puuid)
                account_dto_ex_2 = AccountDTO.from_json(reponse_json)
                print(f"Participant: {account_dto_ex_2.gameName}#{account_dto_ex_2.tagLine}")
            print("\n")