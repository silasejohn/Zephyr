### Global Imports
import sys

### Local Imports
from __init__ import update_sys_path
update_sys_path()
from modules.api_clients.google_client.google_spreadsheet_api import SPREADSHEET_OPS
from modules.utils.color_utils import warning_print, error_print, info_print, success_print

##############################
### SPREADSHEET / SHEET ID ###
##############################
SPREADSHEET_ID = "1uvQafCH4xmiKDgW0lE84AvL1x5n385MU2bIYEaTTR1A"
  # ... get this from the URL of the Google Sheet
TEAM_ID = "WG"  # Team ID 
TEAM_NAME = "Wrap Gods"  # Team Name 

# Initialize the Google Sheets API client
SPREADSHEET_OPS.initialize("WRITE", SPREADSHEET_ID)

# Delete Sheet for Team WG
SPREADSHEET_OPS.delete_sheet("[WG] Wrap Gods")  # delete the sheet for the team if it exists

# Create Sheet for TEAM WG
SHEET_NAME = SPREADSHEET_OPS.create_sheet_for_team(TEAM_ID, TEAM_NAME)  # create a new sheet for the team

# access json file with team data
TEAM_DATA_JSON = f"data/processed/gcs_s2_tourney_scout_info/{TEAM_ID}.json"
player_dict = SPREADSHEET_OPS.get_team_data_from_json(TEAM_DATA_JSON)  # get the team data from the JSON file

# Calculate Player Cell Data
player_data = []

print(f"Processing team: {TEAM_NAME} ({TEAM_ID})")
print(player_dict)
input("Press Enter to continue...")  # wait for user input to continue


for player_disc, player_info in player_dict.items():
    player_discord_username = player_disc
    print(f"Processing player: {player_discord_username}")
    player_rank_score = "UNKNOWN"  # default value if rank is not available
    print(player_info["declared_positions"])

    input("Press Enter to continue...")  # wait for user input to continue
    

    player_declared_roles = "|".join(player_info["declared_positions"])  # join the declared positions with a comma
    player_tourney_roles = player_info["tourney_positions_played_count"]

    for role, times_played in player_tourney_roles.items():
        player_declared_roles += f"||{role}({times_played}g)"  # append the role and times played to the declared roles

    profile_opgg = "\n".join(player_info["player_igns"])  # join the player IGNs with a newline
    profile_log = ""
    for ign in player_info["player_igns"]:
        profile_log += "LOG\n"  # append "LOG" for each IGN in the profile log
    
    player_current_rank = "\n".join(player_info["player_account_current_ranks"])  # join the current ranks with a newline

    player_data.append([
        player_discord_username,  # Player Discord Username
        player_rank_score,         # Player Rank Score
        player_declared_roles,     # Player Declared Roles
        profile_opgg,  # Profile OP.GG
        profile_log,  # Profile LOG
        player_current_rank,  # Current Rank
        "..."   # Peak Rank
    ])

for player in player_data:
    SPREADSHEET_OPS.insert_player_data(TEAM_ID, header_row_num=4, payload=player, start_col_letter="B")  # insert player data into the sheet

sys.exit(0)  # exit the script after editing the cell