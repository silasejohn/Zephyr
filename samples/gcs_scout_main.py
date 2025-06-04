### Global Imports
import sys
from collections import defaultdict

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
# SPREADSHEET_OPS.delete_sheet("[WG] Wrap Gods")  # delete the sheet for the team if it exists

# Create Sheet for TEAM WG
SHEET_NAME = SPREADSHEET_OPS.create_sheet_for_team(TEAM_ID, TEAM_NAME, mode="reset")  # create a new sheet for the team

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
    print(player_info["declared_positions"])    

    player_declared_roles = "|".join(player_info["declared_positions"])  # join the declared positions with a comma
    player_tourney_roles = player_info["tourney_positions_played_count"]

    for role, times_played in player_tourney_roles.items():
        player_declared_roles += f"||{role}({times_played}g)"  # append the role and times played to the declared roles

    profile_opgg = "\n".join(player_info["player_igns"])  # join the player IGNs with a newline
    profile_log = "LOG"
    first_log = False
    for ign in player_info["player_igns"]:
        if not first_log:
            first_log = True
            continue
        profile_log += "\nLOG"  # append "LOG" for each IGN in the profile log
    print(player_info["player_account_current_ranks"])

    # determine player's highest of current rank
    player_current_rank_options = [rank for rank in player_info["player_account_current_ranks"] if rank != "UNKNOWN"]
    max_rank = "??"  # default value if no rank is available

    # determine player's highest current rank (via rank score)
    for rank_text in player_current_rank_options:
        rank_score = SPREADSHEET_OPS.generate_rank_score(rank_text)  # get the rank score from the rank text
        max_rank_score = SPREADSHEET_OPS.generate_rank_score(max_rank)  # get the rank score from the rank text
        if max_rank == "??" or rank_score > max_rank_score:
            max_rank = rank_text

    player_current_rank = max_rank  # set the player's current rank to the highest current rank

    def format_champ_history(player_pos_champ_history):
        role_champ_count = defaultdict(lambda: defaultdict(int))

        # Count how many times each champ is played per role
        for entry in player_pos_champ_history.values():
            role, champ = entry.split("_", 1)
            role_champ_count[role][champ] += 1

        roles_order = ["TOP", "JGL", "MID", "BOT", "SUP"]
        result_strings = ""

        for role in roles_order:
            if role in role_champ_count:
                champs = role_champ_count[role]

                # Calculate total games for this role
                total_games = sum(champs.values())

                # Group champs by game count
                count_groups = defaultdict(list)
                for champ, count in champs.items():
                    count_groups[count].append(champ)

                # Sort and format grouped output
                grouped_output = []
                for count in sorted(count_groups.keys(), reverse=True):
                    champ_list = sorted(count_groups[count])  # alphabetical within group
                    group_str = ", ".join(champ_list) + f" ({count}g)"
                    grouped_output.append(group_str)

                role_str = f"[Tourney - ({role} ~ {total_games}g)] " + " | ".join(grouped_output)
                result_strings += role_str + "\n"

        return result_strings.rstrip()  # remove final newline
    
    tourney_champs_played = format_champ_history(player_info["player_pos_champ_history"]) # .values())


    # # determine player's champs played in tourney by role
    # top_champs = [v for v in player_info["player_pos_champ_history"].values() if v.startswith("TOP_")]
    # jgl_champs = [v for v in player_info["player_pos_champ_history"].values() if v.startswith("JGL_")]
    # mid_champs = [v for v in player_info["player_pos_champ_history"].values() if v.startswith("MID_")]
    # bot_champs = [v for v in player_info["player_pos_champ_history"].values() if v.startswith("BOT_")]
    # sup_champs = [v for v in player_info["player_pos_champ_history"].values() if v.startswith("SUP_")]

    # # sort the champs played by frequency in each list 
    # top_champs.sort(key=lambda x: player_info["player_pos_champ_history"].get(x, 0), reverse=True)
    # jgl_champs.sort(key=lambda x: player_info["player_pos_champ_history"].get(x, 0), reverse=True)
    # mid_champs.sort(key=lambda x: player_info["player_pos_champ_history"].get(x, 0), reverse=True)
    # bot_champs.sort(key=lambda x: player_info["player_pos_champ_history"].get(x, 0), reverse=True)
    # sup_champs.sort(key=lambda x: player_info["player_pos_champ_history"].get(x, 0), reverse=True)
    
    # tourney_champs_played = ""
    # top_champs_played = ""
    # jgl_champs_played = ""
    # mid_champs_played = ""
    # bot_champs_played = ""
    # sup_champs_played = ""
    # if top_champs: 
    #     top_champs_played += f"[Tourney - TOP] "
    #     for champ in top_champs:
    #         top_champs_played += f"{champ[4:]}, "  # remove the "TOP_" prefix from the champ name
    #     top_champs_played = top_champs_played[:-2]  # remove the last comma and space
    #     if top_champs_played != "":
    #         top_champs_played += "\n"
    # if jgl_champs:
    #     jgl_champs_played += f"[Tourney - JGL] "
    #     for champ in jgl_champs:
    #         jgl_champs_played += f"{champ[4:]}, "
    #     jgl_champs_played = jgl_champs_played[:-2]  # remove the last comma and space
    #     if jgl_champs_played != "":
    #         jgl_champs_played += "\n"
    # if mid_champs:
    #     mid_champs_played += f"[Tourney - MID] "
    #     for champ in mid_champs:
    #         mid_champs_played += f"{champ[4:]}, "
    #     mid_champs_player = mid_champs_played[:-2]  # remove the last comma and space
    #     if mid_champs_played != "":
    #         mid_champs_played += "\n"
    # if bot_champs:
    #     bot_champs_played += f"[Tourney - BOT] "
    #     for champ in bot_champs:
    #         bot_champs_played += f"{champ[4:]}, "
    #     bot_champs_played = bot_champs_played[:-2]  # remove the last comma and space
    #     if bot_champs_played != "":
    #         bot_champs_played += "\n"
    # if sup_champs:
    #     sup_champs_played += f"[Tourney - SUP] "
    #     for champ in sup_champs:
    #         sup_champs_played += f"{champ[4:]}, "
    #     sup_champs_played = sup_champs_played[:-2]  # remove the last comma and space

    # tourney_champs_played = top_champs_played + jgl_champs_played + mid_champs_played + bot_champs_played + sup_champs_played

    # if tourney_champs_played.endswith("\n"):
    #     tourney_champs_played = tourney_champs_played[:-1]  # remove the last newline character

    # MATCHA: bold / () / [] various positions + order it from most likely to least likely based on 50 - 25 - 12.5 rule on games played
    # --- above 25% play rate && 5 games = chance for playing a that secondary role. _ if a role has been played in the past 5-10 tourney games to indicate it is possible!
    # MATCHA: add hyperlinks for player IGNs on OP.GG and LOG
    # MATCHA: some method of a custom player rank score
    # MATCHA: some method of sorting the rows by "RANK SCORE" to prioritize players with higher rank scores first 
    # MATCHA: some format of highlighting 5 rows which are the main players for roster for a game
    # MATCHA: peak rank (from OP.GG / LOG) and display it in the sheet

    player_data.append([
        player_discord_username,  # Player Discord Username
        "...",         # Player Rank Score
        player_declared_roles,     # Player Declared Roles
        profile_opgg,  # Profile OP.GG
        profile_log,  # Profile LOG
        player_current_rank,  # Current Rank
        "...",   # Peak Rank
        tourney_champs_played,   # Tourney Champs Played
    ])

for player in player_data:
    SPREADSHEET_OPS.insert_player_data(TEAM_ID, header_row_num=4, payload=player, start_col_letter="B")  # insert player data into the sheet

### STYLING ###
SPREADSHEET_OPS.make_range_bold_underline(TEAM_ID, "B4", "I4")
SPREADSHEET_OPS.auto_resize_columns_to_fit_text(TEAM_ID, "B4", "I20", extra_pixels=10)  
SPREADSHEET_OPS.apply_horizontal_alignment(TEAM_ID, "B4", "H20", alignment="CENTER")
SPREADSHEET_OPS.apply_vertical_alignment(TEAM_ID, "B4", "I20", alignment="MIDDLE")  # vertically center the text in the cells
SPREADSHEET_OPS.make_range_bold(TEAM_ID, "I5", "H20")

sys.exit(0)  # exit the script after editing the cell