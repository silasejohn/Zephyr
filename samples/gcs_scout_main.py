### Global Imports
import sys
from collections import defaultdict

### Local Imports
from __init__ import update_sys_path
update_sys_path()
from modules.scrapers.league_of_graph_scraper import LeagueOfGraphsScraper
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

    # Create Profile_OPGG / Profile_LOG Links
    player_igns = player_info["player_igns"]
    player_opgg_string = ""
    player_log_string = ""
    for ign in player_igns:
        player_opgg_string += ign + "{"
        player_log_string += "LOG" + "{"  # append the "LOG" string for each IGN in the player IGNs"
        opgg_string = f"https://op.gg/lol/summoners/na/{ign.replace('#', '-')}"  # create the OP.GG link for the player IGN
        log_string = f"https://www.leagueofgraphs.com/summoner/na/{ign.replace('#', '-')}" # create the LOG link for the player IGN
        player_opgg_string += opgg_string + "}|"  # append the OP.GG link to the player OP.GG string
        player_log_string += log_string + "}|"  # append the LOG link to the player LOG string
    player_opgg = player_opgg_string.rstrip("|")  # remove the trailing pipe character
    player_log = player_log_string.rstrip("|")  # remove the trailing pipe character

    # determine player's highest of current rank
    print(player_info["player_account_current_ranks"])
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

    # MATCHA: bold / () / [] various positions + order it from most likely to least likely based on 50 - 25 - 12.5 rule on games played
    # MATCHA: change FONT of IGNs column && Champs Played Column (only data)
    # --- above 25% play rate && 5 games = chance for playing a that secondary role. _ if a role has been played in the past 5-10 tourney games to indicate it is possible!
    # MATCHA: add hyperlinks for player IGNs on OP.GG and LOG
    # MATCHA: some method of a custom player rank score
    # MATCHA: some method of sorting the rows by "RANK SCORE" to prioritize players with higher rank scores first 
    # MATCHA: some format of highlighting 5 rows which are the main players for roster for a game
    # MATCHA: peak rank (from OP.GG / LOG) and display it in the sheet
    # MATCHA: always underline roles or champs played in the last 10 games

    player_data.append([
        player_discord_username,  # Player Discord Username
        "...",         # Player Rank Score
        player_declared_roles,     # Player Declared Roles
        player_opgg,  # Profile OP.GG
        player_log,  # Profile LOG
        player_current_rank,  # Current Rank
        "...",   # Peak Rank
        tourney_champs_played,   # Tourney Champs Played
    ])

# ## Obtain Peak Rank (all time)
LeagueOfGraphsScraper.set_up_rewind_lol()  # set up the League of Legends rewind scraper
for player in player_data:
    player_discord_username = player[0]  # get the player discord username
    
    # split the OP.GG into parts by "|" 
    player_accounts = player[3].split("|")  # split the OP.GG link by pipe character
    max_rank = "??"  # default value if no rank is available

    for player_account in player_accounts:
        player_ign = player_account.split("{")[0]  # splice the IGN from the OP.GG link
        print(f"Processing peak rank for player account: {player_discord_username} ({player_ign})")
        LeagueOfGraphsScraper.load_player_profile(player_ign)  # load the player profile from League of Legends rewind scraper
        peak_rank = LeagueOfGraphsScraper.scrape_player_past_peak_ranks()  # scrape the player past peak ranks from League of Legends rewind scraper
        
        info_print(f"Peak Rank Data for {player_discord_username} ({player_ign}): {peak_rank}")  # print the peak rank data for debugging
        
        ranks = list(peak_rank[0].values())

        info_print(f"Peak Ranks for {player_discord_username} ({player_ign}): {ranks}")  # print the peak ranks for debugging

        # standardize the ranks to a common format
        ranks = [SPREADSHEET_OPS.standardize_rank(rank) for rank in ranks]

        info_print(f"Standardized Peak Ranks for {player_discord_username} ({player_ign}): {ranks}")  # print the standardized peak ranks for debugging
        
        # determine the highest rank from the ranks list
        if ranks:
            peak_rank = max(ranks, key=lambda x: SPREADSHEET_OPS.generate_rank_score(x))
            info_print(f"Peak Rank for {player_discord_username} ({player_ign}): {peak_rank}")  # print the peak rank for debugging
        else:
            peak_rank = None

        # compare peak rank to current max rank
        if peak_rank:
            peak_rank_score = SPREADSHEET_OPS.generate_rank_score(peak_rank)
            max_rank_score = SPREADSHEET_OPS.generate_rank_score(max_rank)
            if max_rank == "??" or peak_rank_score > max_rank_score:
                max_rank = peak_rank
                info_print(f"New Max Peak Rank for {player_discord_username} ({player_ign}): {max_rank}")  # print the new max peak rank for debugging
        else:
            warning_print(f"Could not find peak rank for {player_discord_username} ({player_ign})")

    
    if max_rank != "??":
        player[6] = max_rank  # set the peak rank in the player data
    else:
        warning_print(f"Could not find MAX PEAK RANK for {player_discord_username} ({player_ign})")
        player[6] = "..."  # set to UNKNOWN if no peak rank is found
        
        print(f"Player IGN: {player_ign} - Max Peak Rank: {max_rank}")  # print the player IGN and peak rank for debugging 
        
LeagueOfGraphsScraper.close()  # close the League of Legends rewind scraper

## Sort Players by Peak Rank Score
player_data.sort(key=lambda x: SPREADSHEET_OPS.generate_rank_score(x[5]), reverse=True)  # sort players by their current rank score in descending order

## DATA INSERTION ###
for player in player_data:
    SPREADSHEET_OPS.insert_player_data(TEAM_ID, header_row_num=4, payload=player, start_col_letter="B")  # insert player data into the sheet

### STYLING ###
SPREADSHEET_OPS.make_range_bold_underline(TEAM_ID, "B4", "I4")
SPREADSHEET_OPS.auto_resize_columns_to_fit_text(TEAM_ID, "B4", "I20", extra_pixels=10)  
SPREADSHEET_OPS.apply_horizontal_alignment(TEAM_ID, "B4", "H20", alignment="CENTER")
SPREADSHEET_OPS.apply_vertical_alignment(TEAM_ID, "B4", "I20", alignment="MIDDLE")  # vertically center the text in the cells
SPREADSHEET_OPS.make_range_bold(TEAM_ID, "I5", "H20")

sys.exit(0)  # exit the script after editing the cell