
from __init__ import update_sys_path
update_sys_path()

from samples.lepl_1_form_response_process_and_clean import *
from samples.lepl_2_player_scouting_and_scraping import *
from samples.lepl_3_pv_generation import *

# Stage 1 File Paths
stage_1_input_file = 'data/raw/lepl_draft_info.csv'
stage_1_output_file = 'data/processed/lepl_draft_info.csv'

################################################
### LEPL Form Response Processing / Cleaning ###
################################################

form_response_df = import_raw_form_response_csv_info(stage_1_input_file)
processed_df = import_processed_roster_csv_info(stage_1_output_file)

# - Process Discord Username
processed_df = process_lepl_discord_username(form_response_df, processed_df)

# - Process Player Riot ID
processed_df = process_lepl_player_riot_id(form_response_df, processed_df)

# - Team Name
# - Player Position
# - Rank Score
# - Stated Rank
# - True Peak Rank
# - Current Ego Rank
# - S2024 S3 Peak
# - S2024 S2 Peak
# - S2024 S1 Peak
# - S2023 S2 Peak
# - S2023 S1 Peak
# - Player PUUID
# - Player Encrypted Summoner ID
# - Player Encrypted Account ID

############################################
### LEPL Player Scouting / Data Scraping ###
############################################



##########################
### LEPL PV Generation ###
##########################


# output updated CSV file to data/processed

# store as JSON file (for now)

