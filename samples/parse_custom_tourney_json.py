###############
### IMPORTS ###
###############

# global imports
import os, json

# local imports
from __init__ import update_sys_path
update_sys_path()
from modules.api_clients.riot_client.services.account_v1 import ACCOUNT_V1
from models.account_dto import AccountDTO
from constants.constants import Constants

############
### EX 1 ###
############

# # access all json files in /data/custom_examples, and their 'metadata' key and the 'participants' key within it and print 
# for file in os.listdir("data/custom_examples"):
#     if file.endswith(".json"):
#         with open(f"data/custom_examples/{file}") as f:
#             data = json.load(f)
#             print(f"File: {file}")
#             # print(f"Metadata: {data['metadata']}")
#             participants_list = data['metadata']['participants']
#             for participant_puuid in participants_list:
#                 response_code, reponse_json = ACCOUNT_V1.get_account_by_puuid(participant_puuid)
#                 account_dto_ex_2 = AccountDTO.from_json(reponse_json)
#                 print(f"Participant: {account_dto_ex_2.gameName}#{account_dto_ex_2.tagLine}")
#             print("\n")

""""""

############
### EX 2 ###
############

for file in os.listdir("data/official_tourney_games"): 
    if file.startswith("NA1_"):                                     # signifies tourney custom match
        with open(f"data/official_tourney_games/{file}") as f:  
            data = json.load(f)
            participants_list = data['metadata']['participants']
            team_ids = data['team_ids']
            winning_team_id = data['winning_team_id']

            # FILTER
            if "MDFC" not in team_ids:
                continue

            print(f"File: {file}")
            print(f"[Team IDs] {team_ids}")
            print(f"[Winning Team ID] {winning_team_id}")

            # create instance of Constants class
            constants = Constants()

            # picks / info for both teams 
            draft_picks = data['info']['participants']
            for pick in draft_picks:
                champ_name = pick['championName']
                # print(f"Team 1 Pick - Champ Name: {champ_name}")
                individual_position = pick['individualPosition']
                lane = pick['lane']
                riotIdGameName = pick['riotIdGameName']
                riotIdTagline = pick['riotIdTagline']
                role = pick['role']
                summonerName = pick['summonerName']
                teamPosition = pick['teamPosition']
                summonerId = pick['summonerId']
                puuid = pick['puuid']
                
                # print all this information together
                print(f"Draft Pick - Champ Name: {champ_name}, Individual Position: {individual_position}, Lane: {lane}, Riot ID Game Name: {riotIdGameName}, Riot ID Tagline: {riotIdTagline}, Role: {role}, Summoner Name: {summonerName}, Team Position: {teamPosition}")
                
            # bans per team
            team_1_bans = data['info']['teams'][0]['bans']
            team_2_bans = data['info']['teams'][1]['bans']

            # print out the champion names for each ban
            for ban in team_1_bans:
                champ_id = ban['championId']
                print(f"Team 1 Ban - Champ ID: {champ_id}")

                champ_name = constants.get_champion_name(champ_id)
                print(f"Team 1 Ban - Champ Name: {champ_name}")

            # print out the champion names for each ban
            for ban in team_2_bans:
                champ_id = ban['championId']
                print(f"Team 2 Ban - Champ ID: {champ_id}")

                champ_name = constants.get_champion_name(champ_id)
                print(f"Team 2 Ban - Champ Name: {champ_name}")

            # print(f"[Team 1 Bans] {team_1_bans}")
            # print(f"[Team 2 Bans] {team_2_bans}")

            # for participant_puuid in participants_list:
            #     response_code, reponse_json = ACCOUNT_V1.get_account_by_puuid(participant_puuid)
            #     account_dto_ex_2 = AccountDTO.from_json(reponse_json)
            #     print(f"Participant: {account_dto_ex_2.gameName}#{account_dto_ex_2.tagLine}")
            print("\n")