
# global imports
import pandas as pd
import os, sys

# local imports
from __init__ import update_sys_path
update_sys_path()

# unique print inports
from modules.utils.color_utils import warning_print, error_print, info_print, success_print

################################################
### LEPL Form Response Processing / Cleaning ###
################################################

def import_raw_form_response_csv_info(input_file):
    df = pd.read_csv(input_file)
    return df

def import_processed_roster_csv_info(input_file):
    # if iput_file does not exist, create a new dataframe
    if not os.path.exists(input_file):
        # log that the file does not exist
        warning_print(f'File {input_file} does not exist. Creating a new dataframe.')
        df = pd.DataFrame(columns=['Discord Username', 'Player Riot ID', 'Team Name', 'Player Position', 'Rank Score', 'Stated Rank', 'True Peak Rank', 'Current Ego Rank', 'S2024 S3 Peak', 'S2024 S2 Peak', 'S2024 S1 Peak', 'S2023 S2 Peak', 'S2023 S1 Peak', 'Player PUUID', 'Player Encrypted Summoner ID', 'Player Encrypted Account ID'])
        # export the dataframe to a CSV file
        df.to_csv(input_file, index=False)
        return df
    
    # if input_file exists, read the CSV file and return the dataframe
    df = pd.read_csv(input_file)
    return df

def process_lepl_discord_username(form_response_df, processed_df):
    # check if the column exists in the dataframe
    if 'Discord Username' in form_response_df.columns:
        # ensure that every value in the column exists
        if form_response_df['Discord Username'].isnull().values.any():
            # find the exact row where the null value is located
            null_row = form_response_df[form_response_df['Discord Username'].isnull()].index[0]
            # log error message (be specific)
            error_print('Column Discord Username contains null values. Please fill in all Discord usernames.')
            warning_print(f'Null values found in the following row: {null_row}.')
            warning_print('Exiting program.')
            sys.exit(1)

        # add all discord usernames to the processed_df dataframe (that are not already in the dataframe)
        for discord_username in form_response_df['Discord Username']:
            if discord_username not in processed_df['Discord Username'].values:
                new_row = {'Discord Username': discord_username}
                processed_df = pd.concat([processed_df, pd.DataFrame([new_row])], ignore_index=True)
                info_print(f'Added Discord Username {discord_username} to the processed_df dataframe.')
            else:
                warning_print(f'Discord Username {discord_username} already exists in the processed_df dataframe.') 
        
        success_print('Discord Username column processed successfully.')
        return processed_df
    else:
        # if the column does not exist, log error message
        error_print(f'Column Discord Username does not exist in the form_response_df dataframe.')
        sys.exit(1)

def process_lepl_player_riot_id():
    pass