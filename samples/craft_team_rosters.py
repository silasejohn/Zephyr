# this file will craft and create a json file for each team (16 total) in GCS tournament
# each player will have (1) puuid (2) encrypted summoner id (3) riot id & tag (4) roles played in tourney

# ###############
# ### IMPORTS ###
# ###############

# global imports
import os, json, sys

# local imports
from __init__ import update_sys_path
update_sys_path()

from modules.api_clients.riot_client.services.account_v1 import ACCOUNT_V1
from modules.api_clients.riot_client.services.summoner_v4 import SUMMONER_V4

from constants.constants import Constants
from models.account_dto import AccountDTO
from models.summoner_dto import SummonerDTO
from models.league_draft_dto import LeagueDraftDTO
from modules.utils.file_utils import save_json_to_file

def update_team_roster_info(team_id: str = None):

    if not team_id:
        print(f"[ERROR] No team_id provided")
        return

    # load existing GCS team data
    constants = Constants()
    teams = constants.GCS_TEAMS

    # filter by team_id if provided
    teams = teams[team_id]

    # create output json
    output_file_name = f"constants/teams/{team_id}.json"

    # edit teams json
    roster = teams["rosters"] # list of players

    ### [STEP 1] Update Player PUUIDs for New Players (as needed) ###
    isUpdated, roster = identify_new_player_puuid(roster) # updates the player_puuid in json if not already updated
    
    # update teams json, new copy of roster to use
    teams["rosters"] = roster 
    roster = teams["rosters"] 
    
    if isUpdated: # update original json too if needed
        print(f"Updating original json for some player puuids for team: {team_id}")
        constants.GCS_TEAMS[team_id] = teams
        constants.update_original_json("GCS_TEAMS")
    else:
        print(f"\nNo puuid updates needed for team: {team_id}")

    ### [STEP 2] Update Player Riot IDs (if changed from previous iteration) ###
    updatedRiotIDs, roster = update_player_riot_id(roster) # updates the player_riot_id in json if not already updated

    if updatedRiotIDs[0] != "":
        for updatedIDs in updatedRiotIDs:
            if updatedIDs == "":
                continue
            print(f"Player Riot ID updated: {updatedIDs}")
            # wait for user input
            input("Press Enter to continue...")
    
    input("\nPress Enter to continue...")
        
    # update teams json, new copy of roster to use
    teams["rosters"] = roster 
    roster = teams["rosters"] 

    if updatedRiotIDs: # update original json too if needed
        print(f"Updating original json for RIOT IDS for team: {team_id}")
        constants.GCS_TEAMS[team_id] = teams
        constants.update_original_json("GCS_TEAMS")
    else:
        print(f"\nNo riot id updates needed for team: {team_id}")

    ### [STEP 3] Update Player SummonerID and AccountID (if changed from previous iteration) ###
    updatedSummonerIDs, updatedAccountIDs, roster = update_player_summoner_and_account_ids(roster) 

    for updatedIDs in updatedSummonerIDs:
        if updatedIDs == "":
            continue
        print(f"Player Summoner ID updated: {updatedIDs}")
        # wait for user input
        input("Press Enter to continue...")
    
    for updatedIDs in updatedAccountIDs:
        if updatedIDs == "":
            continue
        print(f"Player Account ID updated: {updatedIDs}")
        # wait for user input
        input("Press Enter to continue...")
    
    # update teams json, new copy of roster to use
    teams["rosters"] = roster 
    roster = teams["rosters"] 

    if updatedSummonerIDs or updatedAccountIDs: # update original json too if needed
        print(f"Updating original json for SUMMONER / ACCOUNT IDS for team: {team_id}")
        constants.GCS_TEAMS[team_id] = teams
        constants.update_original_json("GCS_TEAMS")
    else:
        print(f"\nNo SUMMONER / ACCOUNT id updates needed for team: {team_id}")

    # MATCHA: Why does ACCOUNT_ID change on every run?

    # MATCHA: code that AUTO pulls their peak rank & current rank (games, roles, champs played those seasons)

    # MATCHA: code that auto goes through .json custom files + pulls the roles that they have played
    #   MATCHA: role / position / champ played / bans they took in previous custom matches (against which team too)

    # MATCHA: code that handles printing all this to google spreadsheet

    # store teams into output json file
    save_json_to_file(teams, output_file_name)
    
    return
    
def identify_new_player_puuid(roster_json):
    print("\n\n[STEP 1] Identify New Player PUUIDs for New Players (as needed)")

    # flag to determine if original json needs to be updated
    first_update = False

    # iterate through each player on a team
    for player in roster_json:
        # use riot id to determine permanent puuid if not already provided
        print(f"<Player Riot ID> {player['player_riot_id']} ... <Rank Score> {player['rank_score']}")    # riot id is the snapshot of players current in game identifier
        
        ### Obtain puuid from riot id if not already provided ###
        if player["player_puuid"] == "%" or player["player_puuid"] == "":
            # ensure that player_riot_id is provided
            if player["player_riot_id"] == "%" or player["player_riot_id"] == "NAME#TAG" or player["player_riot_id"] == "%":
                print(f"[ERROR] No player_riot_id provided for player: {player}")
                return
            else:
                print(f"[INFO] No player_puuid provided for player: {player['player_riot_id']}")
            
            # obtain player puuid via Riot API Account_V1
            player_riot_id = player["player_riot_id"]

            player_riot_id_list = []
            player_puuid_list = []
            if "|" in player_riot_id:
                player_riot_id_list = player_riot_id.split("|")
            else:
                # if its str
                if type(player_riot_id) == str:
                    player_riot_id_list = [player_riot_id]
                else:
                    player_riot_id_list = player_riot_id # if its alr a list

            print(f"Raw Player Riot IDs: {player_riot_id}")
            print(f"Player Riot IDs: {player_riot_id_list}")
            
            for player_riot_id in player_riot_id_list:
                gameName, tagLine = player_riot_id.split("#")
                _, response_json = ACCOUNT_V1.get_account_by_riot_id(gameName, tagLine)
                account_dto = AccountDTO.from_json(response_json)
                player_puuid_list.append(account_dto.puuid)    # get puuid from account_dto

            # store updated information + set flag to modify original json as needed
            player["player_puuid"] = player_puuid_list
            print(f"Player PUUID: {player['player_puuid']}\n")

            # set flag to update original json
            first_update = True

    return first_update, roster_json

def update_player_riot_id(roster_json):
    print("\n\n[STEP 2] Update Player Riot IDs (if changed from previous iteration)")
    # Update Riot ID (if has changed from previous iteration)
    riot_id_updates = []

    for player in roster_json:
        print("\n-------------------------------------")
        print (f"Updating Player Riot IDs for Player: {player['player_riot_id']}")
        print("-------------------------------------")

        # stores multiple accounts per player
        old_player_riot_id_list = player["player_riot_id"]
        player_puuid_list = player["player_puuid"]
        if type(player_puuid_list) == str:
            player_puuid_list = [player_puuid_list]
        new_player_riot_id_list = []

        print(f"\nPulling Player Info for all Accounts...")
        print(f"\tPlayer PUUIDs: {player_puuid_list}")
        print(f"\tPlayer Riot IDs (old): {old_player_riot_id_list}")

        for account_idx in range(len(player_puuid_list)): # iterates from 0 to len(player_puuid_list) - 1
            print(f"\nUpdating Account {account_idx + 1} of {len(player_puuid_list)}")
            _, response_json = ACCOUNT_V1.get_account_by_puuid(player_puuid_list[account_idx])
            account_dto = AccountDTO.from_json(response_json)
            new_player_riot_id = f"{account_dto.gameName}#{account_dto.tagLine}"
            new_player_riot_id_list.append(new_player_riot_id)

            if type(old_player_riot_id_list) == str:
                old_player_riot_id = old_player_riot_id_list
            elif len(old_player_riot_id_list) == 1:
                old_player_riot_id = old_player_riot_id_list[0]
            else:
                old_player_riot_id = old_player_riot_id_list[account_idx]
            
            if old_player_riot_id != new_player_riot_id_list[account_idx]:
                print(f"[Account {account_idx + 1}] {old_player_riot_id} ~> {new_player_riot_id_list[account_idx]}")
                # get user input
                input("Press Enter to Acknowledge Riot ID Change...")
            else:
                print(f"[Account {account_idx + 1}] No change in player_riot_id ({new_player_riot_id_list[account_idx]})")

        # update player_riot_id in json
        combined_ids = ""
        for account_idx in range(len(player_puuid_list)):
            if type(old_player_riot_id_list) == str:
                old_player_riot_id = old_player_riot_id_list
            elif len(old_player_riot_id_list) == 1:
                old_player_riot_id = old_player_riot_id_list[0]
            else:
                old_player_riot_id = old_player_riot_id_list[account_idx]

            if old_player_riot_id != new_player_riot_id_list[account_idx]:
                combined_ids += "{" + str(old_player_riot_id) + "~>" + str(new_player_riot_id_list[account_idx]) + "}"
        riot_id_updates.append(combined_ids)

        # update player_riot_id in json
        player["player_riot_id"] = new_player_riot_id_list
        
    return riot_id_updates, roster_json

def update_player_summoner_and_account_ids(roster_json):
    print("\n\n[STEP 3] Update Player SummonerID and AccountID (if changed from previous iteration)")
    # Update Summoner / Account ID (if has changed from previous iteration)
    riot_summmoner_id_updates = []
    riot_account_id_updates = []

    for player in roster_json:
        print("\n-------------------------------------")
        print (f"Updating Summoner & Account IDs for Player: {player['player_riot_id']}")
        print("-------------------------------------")

        player_puuid_list = player["player_puuid"]
        if type(player_puuid_list) == str:
            player_puuid_list = [player_puuid_list]
        old_player_account_id_list = player["player_encrypted_account_id"]
        old_player_summoner_id_list = player["player_encrypted_summoner_id"]
        new_player_account_id_list = []
        new_player_summoner_id_list = []
        
        # iterate through each player account 
        for account_idx in range(len(player_puuid_list)):
            print(f"Updating Account {account_idx + 1} of {len(player_puuid_list)}")
            _, response_json = SUMMONER_V4.get_summoner_info_by_puuid(player_puuid_list[account_idx])
            summoner_dto = SummonerDTO.from_json(response_json)
            new_player_account_id_list.append(summoner_dto.encryptedAccountId)
            new_player_summoner_id_list.append(summoner_dto.encryptedSummonerID)

        ##########################
        ### ACCOUNT ID UPDATES ###
        ##########################
        # if Account ID doesn't previously exist ... update with new account ids
        if old_player_account_id_list == "%" or old_player_account_id_list == "" or old_player_account_id_list[0] == "":
            # update account id in json
            player["player_encrypted_account_id"] = new_player_account_id_list

            # store updated information
            new_id_msg = ""
            for account_idx in range(len(player_puuid_list)):
                print(f"[Account {account_idx + 1}] % ~> {new_player_account_id_list[account_idx]}")
                new_id_msg += "{" + f"% -> {str(new_player_account_id_list[account_idx])}" + "}"
            riot_account_id_updates.append(new_id_msg)

        else: # if Account ID already exists, compare and update if needed
            for account_idx in range(len(player_puuid_list)):
                if type(old_player_account_id_list) == str:
                    old_player_account_id = old_player_account_id_list
                elif len(old_player_account_id_list) == 1:
                    old_player_account_id = old_player_account_id_list[0]
                else:
                    old_player_account_id = old_player_account_id_list[account_idx]

                if old_player_account_id != new_player_account_id_list[account_idx]:
                    print(f"[Account {account_idx + 1}] {old_player_account_id} ~> {new_player_account_id_list[account_idx]}")
                else:
                    print(f"[Account {account_idx + 1}] No change in player_encrypted_account_id ({new_player_account_id_list[account_idx]})")
            
            # update account id in json
            combined_ids = ""
            for account_idx in range(len(player_puuid_list)):
                if type(old_player_account_id_list) == str:
                    old_player_account_id = old_player_account_id_list
                elif len(old_player_account_id_list) == 1:
                    old_player_account_id = old_player_account_id_list[0]
                else:
                    old_player_account_id = old_player_account_id_list[account_idx]

                if old_player_account_id != new_player_account_id_list[account_idx]:
                    combined_ids += "{" + str(old_player_account_id) + "~>" + str(new_player_account_id_list[account_idx]) + "}"
            riot_account_id_updates.append(combined_ids)

            # update account id in json
            player["player_encrypted_account_id"] = new_player_account_id_list

        ###########################
        ### SUMMONER ID UPDATES ###
        ###########################
        # if Summoner ID doesn't previously exist ... update with new summoner ids
        if old_player_summoner_id_list == "%" or old_player_summoner_id_list == "" or old_player_summoner_id_list[0] == "":
            # update summoner id in json
            player["player_encrypted_summoner_id"] = new_player_summoner_id_list

            # store updated information
            new_id_msg = ""
            for account_idx in range(len(player_puuid_list)):
                print(f"[Account {account_idx + 1}] % ~> {new_player_summoner_id_list[account_idx]}")
                new_id_msg += "{" + f"% -> {str(new_player_summoner_id_list[account_idx])}" + "}"
            riot_summmoner_id_updates.append(new_id_msg)

        else: # if Summoner ID already exists, compare and update if needed
            for account_idx in range(len(player_puuid_list)):
                if type(old_player_summoner_id_list) == str:
                    old_player_summoner_id = old_player_summoner_id_list
                elif len(old_player_summoner_id_list) == 1:
                    old_player_summoner_id = old_player_summoner_id_list[0]
                else:
                    old_player_summoner_id = old_player_summoner_id_list[account_idx]

                if old_player_summoner_id != new_player_summoner_id_list[account_idx]:
                    print(f"[Account {account_idx + 1}] {old_player_summoner_id} ~> {new_player_summoner_id_list[account_idx]}")
                else:
                    print(f"[Account {account_idx + 1}] No change in player_summoner_id ({new_player_summoner_id_list[account_idx]})")
            
            # update account id in json
            combined_ids = ""
            for account_idx in range(len(player_puuid_list)):
                if type(old_player_summoner_id_list) == str:
                    old_player_summoner_id = old_player_summoner_id_list
                elif len(old_player_summoner_id_list) == 1:
                    old_player_summoner_id = old_player_summoner_id_list[0]
                else:
                    old_player_summoner_id = old_player_summoner_id_list[account_idx]
                if old_player_summoner_id != new_player_summoner_id_list[account_idx]:
                    combined_ids += "{" + str(old_player_summoner_id) + "~>" + str(new_player_summoner_id_list[account_idx]) + "}"
            riot_summmoner_id_updates.append(combined_ids)

            # update account id in json
            player["player_encrypted_account_id"] = new_player_summoner_id_list
    return riot_summmoner_id_updates, riot_account_id_updates, roster_json

update_team_roster_info("V8")