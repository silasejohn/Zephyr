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
from models.league_draft_dto import LeagueDraftDTO

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

def parse_custom_match_info_by_team_id(team_id: str = None, optional_opponent_team_id: str = None):
    if not team_id:
        print(f"[ERROR] No team_id provided")
        return
    
    for file in os.listdir("data/official_tourney_games"): 
        if file.startswith("NA1_"):                                     # signifies tourney custom match
            with open(f"data/official_tourney_games/{file}") as f:  
                data = json.load(f)

                ### TEAM ID VALIDATION ##
                team_ids = data['team_ids']

                # check if team_id is in team_ids
                if optional_opponent_team_id:
                    # check if both team_id and optional_opponent_team_id are in team_ids
                    if team_id not in team_ids or optional_opponent_team_id not in team_ids:
                        continue
                else:
                    # check if team_id is in team_ids
                    if team_id not in team_ids:
                        continue

                ## DATA EXTRACTION ##

                # get match_ID, participants, team_ids, winning_team_id
                gcs_id_long = file.replace(".json", "").replace("match", "M").split("_")[2:]
                gcs_id = "_".join(gcs_id_long).replace("_", "")
                match_id = data['metadata']['matchId']
                winning_team_id = data['winning_team_id']

                print(f"File: {file}")
                print(f"[Team IDs] {team_ids}")
                print(f"[Winning Team ID] {winning_team_id}")

                ## SIDE DETERMINATION ##

                participants_list = data['metadata']['participants']
                blue_side_player_puuids = participants_list[:5]
                red_side_player_puuids = participants_list[5:]

                team_id_is_blue = [False, ""]
                team_id_is_red = [False, ""]
                
                for puuid in blue_side_player_puuids:
                    # open json file constants/teams/{team_id}.json 
                    with open(f"constants/teams/{team_id}.json") as f:
                        # load json file
                        team_data = json.load(f)
                        # get team roster
                        team_roster = team_data['rosters']

                        # get player info
                        for player in team_roster:
                            if player['player_puuid'] == puuid:
                                print(f"Blue Side Player: {player['player_riot_id']}")
                                team_id_is_blue = [True, team_id]
                
                for puuid in red_side_player_puuids:
                    # open json file constants/teams/{team_id}.json 
                    with open(f"constants/teams/{team_id}.json") as f:
                        # load json file
                        team_data = json.load(f)
                        # get team roster
                        team_roster = team_data['rosters']

                        # get player info
                        for player in team_roster:
                            if player['player_puuid'] == puuid:
                                print(f"Red Side Player: {player['player_riot_id']}")
                                team_id_is_red[0] = [True, team_id]

                if team_id_is_blue:
                    # determine other team_id that is not team_id_is_blue[1]
                    if team_id_is_blue[1] == team_ids[0]:
                        other_team_id = team_ids[1]
                    else:
                        other_team_id = team_ids[0]
                    team_id_is_red = [False, other_team_id]
                    print(f"[{team_id} is Blue Side]")
                elif team_id_is_red:
                    if team_id_is_red[1] == team_ids[0]:
                        other_team_id = team_ids[1]
                    else:
                        other_team_id = team_ids[0]
                    team_id_is_blue = [False, other_team_id]
                    print(f"[{team_id} is Red Side]")
                else:
                    print(f"[{team_id} is not in this match]")

                # create instance of Constants class
                constants = Constants()

                # Create instance of LeagueDraftDTO
                # make sure blue / red are the right side of the draft
                # league_draft_dto = LeagueDraftDTO(
                #     gcs_id=gcs_id,
                #     match_id=match_id,
                #     blue_team_id=data['team_ids'][0],  # MATCHA team_ids[0] could be blue or red side not sure yet
                #     red_team_id=data['team_ids'][1]
                # )

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
                    print(f"Draft Pick - Champ Name: {champ_name}, Individual Position: {individual_position}, Lane: {lane}, Riot ID Game Name: {riotIdGameName}, Riot ID Tagline: {riotIdTagline}, Role: {role}, Summoner Name: {summonerName}, Team Position: {teamPosition}\n")
                    
                # bans per team
                blue_bans = data['info']['teams'][0]['bans']
                red_bans = data['info']['teams'][1]['bans']

                # Blue Ban 1 (pickTurn 1), Blue Ban 2 (pickTurn 3), Blue Ban 3 (pickTurn 5)
                blue_ban_1 = constants.get_champion_name([ban['championId'] for ban in blue_bans if ban['pickTurn'] == 1][0])
                blue_ban_2 = constants.get_champion_name([ban['championId'] for ban in blue_bans if ban['pickTurn'] == 3][0])
                blue_ban_3 = constants.get_champion_name([ban['championId'] for ban in blue_bans if ban['pickTurn'] == 5][0])
                
                # print out the blue bans
                print(f"\n<{team_id_is_blue[1]}> [Blue Ban Phase 1]")
                print(f"\t{blue_ban_1} | {blue_ban_2} | {blue_ban_3}")

                # Red Ban 1 (pickTurn 2), Red Ban 2 (pickTurn 4), Red Ban 3 (pickTurn 6)
                red_ban_1 = constants.get_champion_name([ban['championId'] for ban in red_bans if ban['pickTurn'] == 2][0])
                red_ban_2 = constants.get_champion_name([ban['championId'] for ban in red_bans if ban['pickTurn'] == 4][0])
                red_ban_3 = constants.get_champion_name([ban['championId'] for ban in red_bans if ban['pickTurn'] == 6][0])
                print(f"\n<{team_id_is_red[1]}> [Red Ban Phase 1]")
                print(f"\t{red_ban_1} | {red_ban_2} | {red_ban_3}")

                # Draft Picks (Blue & Red)
                print(f"\n[Blue Draft Picks] In Progress...")
                print(f"[Red Draft Picks] In Progress...")

                # Blue Ban 4 (pickTurn 1), Blue Ban 5 (pickTurn 3)
                blue_ban_4 = constants.get_champion_name(blue_bans[3]['championId'])
                blue_ban_5 = constants.get_champion_name(blue_bans[4]['championId'])
                print(f"\n<{team_id_is_blue[1]}> [Blue Ban Phase 2]")
                print(f"\t{blue_ban_4} | {blue_ban_5}")

                # Red Ban 4 (pickTurn 2), Red Ban 5 (pickTurn 4)
                red_ban_4 = constants.get_champion_name(red_bans[3]['championId'])
                red_ban_5 = constants.get_champion_name(red_bans[4]['championId'])
                print(f"\n<{team_id_is_red[1]}> [Red Ban Phase 2]")
                print(f"\t{red_ban_4} | {red_ban_5}")
   
                print("\n")

parse_custom_match_info_by_team_id("V8", "AWB")