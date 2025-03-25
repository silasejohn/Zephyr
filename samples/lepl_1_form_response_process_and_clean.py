
from __init__ import update_sys_path
update_sys_path()

from modules.lepl_functions.lepl_data_manipulation import create_df_lepl_form_responses, create_lepl_roster_csv_from_df

################################################
### LEPL Form Response Processing / Cleaning ###
################################################

# input CSV as DF file
input_file = 'data/raw/lepl_draft_info.csv'
output_file = 'data/processed/lepl_draft_info.csv'

df = create_df_lepl_form_responses(input_file)

# process each column of the draft_info CSV file

# - Discord Username

# - Player Riot ID
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
create_lepl_roster_csv_from_df(df, output_file)


# store as JSON file (for now)

