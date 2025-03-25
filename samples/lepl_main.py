
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

# (1) Process Player Riot ID
processed_df = process_lepl_player_riot_id(form_response_df, processed_df)

# (2) Process Team Name
### NO NEED

# (3) Process Stated Player Position
processed_df = process_lepl_stated_player_position(form_response_df, processed_df)

# (4) Process Rank Score
### NO NEED

# (5) Process Stated Current / Peak Rank
processed_df = process_lepl_stated_rank(form_response_df, processed_df)

# (6) Process True Peak Rank
### ... IN PROGRESS

# (7) Process Current Ego Rank
### ... IN PROGRESS

# (8) Process Peak Rank for S2024 S3, S2024 S2, S2024 S1, S2023 S2, S2023 S1
### ... IN PROGRESS

# (9) Process Player PUUID, Encrypted Summoner ID, Encrypted Account ID
### ... IN PROGRESS

export_processed_roster_csv_info(stage_1_output_file, processed_df)

############################################
### LEPL Player Scouting / Data Scraping ###
############################################



##########################
### LEPL PV Generation ###
##########################


# output updated CSV file to data/processed

# store as JSON file (for now)

