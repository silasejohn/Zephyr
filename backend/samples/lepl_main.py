
from __init__ import update_sys_path
update_sys_path()

from samples.lepl_1_form_response_process_and_clean import *
from samples.lepl_2_player_scouting_and_scraping import *
from samples.lepl_3_pv_generation import *

# Stage 1 File Paths
stage_1_input_file = '../data/raw/lepl_draft_info.csv'
stage_1_output_file = '../data/processed/lepl_draft_info_stage_1.csv'
stage_2_output_file = '../data/processed/lepl_draft_info_stage_2.csv'
stage_3_output_file = '../data/processed/lepl_draft_info_stage_3.csv'

################################################
### LEPL Form Response Processing / Cleaning ###
################################################
OPGG_SCRAPE = False
LOG_RANK_SCRAPE = False

form_response_df = import_raw_form_response_csv_info(stage_1_input_file)
processed_df = import_processed_roster_csv_info(stage_1_output_file)

# (1) Process Discord Username
processed_df = process_lepl_discord_username(form_response_df, processed_df)

# (2) Process Player Riot ID
processed_df = process_lepl_player_riot_id(form_response_df, processed_df, stage_1_output_file, OPGG_SCRAPE)

# (3) Process Team Name
### NO NEED

# (4) Process Stated Player Position
processed_df = process_lepl_stated_player_position(form_response_df, processed_df)

# (5) Process Rank Diff Score
### NO NEED

# (6) Process Stated Current / Peak Rank
processed_df = process_lepl_stated_rank(form_response_df, processed_df) 

# (7) Process True Peak Rank, Current Ego Rank, Peak Rank for S2024 S3, S2024 S2, S2024 S1, S2023 S2, S2023 S1
processed_df = process_lepl_true_rank(form_response_df, processed_df, stage_1_output_file, LOG_RANK_SCRAPE)

# (8) Process Player PUUID, Encrypted Summoner ID, Encrypted Account ID
### ... IN PROGRESS ... but don't need right now!

# Finalize the Processed Export
export_processed_roster_csv_info(stage_1_output_file, processed_df)

############################################
### LEPL Player Scouting / Data Scraping ###
############################################

# import the stage 1 output file
processed_df = import_processed_roster_csv_info(stage_1_output_file)

# (9) Scrape Rewind.Lol for Player Stats


# export the processed roster CSV file
export_processed_roster_csv_info(stage_2_output_file, processed_df)

##########################
### LEPL PV Generation ###
##########################

# import the stage 2 output file
processed_df = import_processed_roster_csv_info(stage_2_output_file)


# (C1) Generate Point Stats
s3_processed_df = generate_lepl_rank_points_stats(processed_df, stage_3_output_file)

export_processed_roster_csv_info(stage_3_output_file, s3_processed_df)

# output updated CSV file to data/processed

# store as JSON file (for now)

