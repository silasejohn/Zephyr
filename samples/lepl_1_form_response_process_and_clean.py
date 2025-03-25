
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
        df = pd.DataFrame(columns=['Discord Username', 'Player Riot ID', 'Team Name', 'Rank Score', 'Stated Player Pos', 'True Player Pos', 'Stated Current Rank', 'Stated Peak Rank', 'True Peak Rank', 'Current Ego Rank', 'S2024 S3 Peak', 'S2024 S2 Peak', 'S2024 S1 Peak', 'S2023 S2 Peak', 'S2023 S1 Peak', 'Player PUUID', 'Player Encrypted Summoner ID', 'Player Encrypted Account ID'])
        # export the dataframe to a CSV file
        df.to_csv(input_file, index=False)
        return df
    
    # if input_file exists, read the CSV file and return the dataframe
    df = pd.read_csv(input_file)
    return df

def export_processed_roster_csv_info(output_file, processed_df):
    processed_df.to_csv(output_file, index=False)
    success_print(f'Processed roster information exported to {output_file}.')
    return

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

def process_lepl_player_riot_id(form_response_df, processed_df):
    return processed_df

def process_lepl_stated_player_position(form_response_df, processed_df):
    
    # pull positions from form_response_df
    pos_list = ["TOP", "JGL", "MID", "BOT", "SUP"]

    # avoid modifying the original dataframe
    form_response_df = form_response_df.copy()

    # take slice of "Discord Username" and "Primary Role" and "Secondary Role" columns
    form_response_df = form_response_df[['Discord Username', 'Primary Role', 'Secondary Role']]
    
    # replace all NaN values with empty strings for Primary Role and Secondary Role Columns
    form_response_df['Primary Role'] = form_response_df['Primary Role'].fillna('')
    form_response_df['Secondary Role'] = form_response_df['Secondary Role'].fillna('')

    # turn all potential POS into uppercase
    form_response_df['Primary Role'] = form_response_df['Primary Role'].str.upper()
    form_response_df['Secondary Role'] = form_response_df['Secondary Role'].str.upper()

    # if "ADC" then replace with "BOT"
    form_response_df['Primary Role'] = form_response_df['Primary Role'].replace('ADC', 'BOT')
    form_response_df['Secondary Role'] = form_response_df['Secondary Role'].replace('ADC', 'BOT')

    # if "SUPPORT" then replace with "SUP"
    form_response_df['Primary Role'] = form_response_df['Primary Role'].replace('SUPPORT', 'SUP')
    form_response_df['Secondary Role'] = form_response_df['Secondary Role'].replace('SUPPORT', 'SUP')

    # if "JUNGLE" then replace with "JGL"
    form_response_df['Primary Role'] = form_response_df['Primary Role'].replace('JUNGLE', 'JGL')
    form_response_df['Secondary Role'] = form_response_df['Secondary Role'].replace('JUNGLE', 'JGL')

    # add primary role & secondary role seperated by "|" to a column "Stated Player Pos" in processed_df
    # add each primary pos + secondary pos in each row to a list, then add that list to column "Stated Player Pos" in processed_df
    for index, row in form_response_df.iterrows():
        # create a list of all stated positions
        stated_pos_list = []
        primary_roles = []
        secondary_roles = []
        if "|" in row['Primary Role']:
            primary_roles = row['Primary Role'].split("|")
            for primary_role in primary_roles:
                if primary_role in pos_list:
                    stated_pos_list.append(primary_role)

        if "|" in row['Secondary Role']:
            secondary_roles = row['Secondary Role'].split("|")
            for secondary_role in secondary_roles:
                if secondary_role in pos_list:
                    stated_pos_list.append(secondary_role)

        if row['Primary Role'] in pos_list:
            stated_pos_list.append(row['Primary Role'])

        if row['Secondary Role'] in pos_list:
            stated_pos_list.append(row['Secondary Role'])

        stated_pos_string = '|'.join(stated_pos_list)
        processed_df.loc[processed_df['Discord Username'] == row['Discord Username'], 'Stated Player Pos'] = stated_pos_string

    return processed_df

def process_lepl_stated_rank(form_response_df, processed_df):

    # pull ranks from form_response_df
    rank_list = ["Unranked", "Iron 4", "Iron 3", "Iron 2", "Iron 1", "Bronze 4", "Bronze 3", "Bronze 2", "Bronze 1", "Silver 4", "Silver 3", "Silver 2", "Silver 1", "Gold 4", "Gold 3", "Gold 2", "Gold 1", "Platinum 4", "Platinum 3", "Platinum 2", "Platinum 1", "Emerald 4", "Emerald 3", "Emerald 2", "Emerald 1","Diamond 4", "Diamond 3", "Diamond 2", "Diamond 1", "Master", "Grandmaster", "Challenger"]
    
    # take slice of "Discord Username" and "Rank" columns

    form_response_slice_df = form_response_df[['Discord Username', 'Current Rank', 'Peak Rank']]
    form_response_slice_df = form_response_slice_df.copy()

    # replace all NaN values with empty strings for Rank Column
    form_response_slice_df['Current Rank'] = form_response_slice_df['Current Rank'].fillna('Unranked')
    form_response_slice_df['Peak Rank'] = form_response_slice_df['Peak Rank'].fillna('Unranked')

    # turn all potential ranks into Camelcase
    form_response_slice_df['Current Rank'] = form_response_slice_df['Current Rank'].str.title()
    form_response_slice_df['Peak Rank'] = form_response_slice_df['Peak Rank'].str.title()

    # replace "Plat" with "Platinum"
    form_response_slice_df['Current Rank'] = form_response_slice_df['Current Rank'].replace('Plat 4', 'Platinum 4')
    form_response_slice_df['Peak Rank'] = form_response_slice_df['Peak Rank'].replace('Plat 4', 'Platinum 4')
    form_response_slice_df['Current Rank'] = form_response_slice_df['Current Rank'].replace('Plat 3', 'Platinum 3')
    form_response_slice_df['Peak Rank'] = form_response_slice_df['Peak Rank'].replace('Plat 3', 'Platinum 3')
    form_response_slice_df['Current Rank'] = form_response_slice_df['Current Rank'].replace('Plat 2', 'Platinum 2')
    form_response_slice_df['Peak Rank'] = form_response_slice_df['Peak Rank'].replace('Plat 2', 'Platinum 2')
    form_response_slice_df['Current Rank'] = form_response_slice_df['Current Rank'].replace('Plat 1', 'Platinum 1')
    form_response_slice_df['Peak Rank'] = form_response_slice_df['Peak Rank'].replace('Plat 1', 'Platinum 1')
    form_response_slice_df['Current Rank'] = form_response_slice_df['Current Rank'].replace('Masters', 'Master')
    form_response_slice_df['Peak Rank'] = form_response_slice_df['Peak Rank'].replace('Masters', 'Master')

    # ensure that all ranks are in the rank_list, if not log error message
    for rank in form_response_slice_df['Current Rank']:
        if rank not in rank_list:
            error_print(f'Rank {rank} is not in the rank list.')
            sys.exit(1)

    # export cleaned formed_response_df "Current Rank" and "Peak Rank" to processed_df 'Stated Current Rank' and 'Stated Peak Rank' based on 'Discord Username'
    for index, row in form_response_slice_df.iterrows():
        processed_df.loc[processed_df['Discord Username'] == row['Discord Username'], 'Stated Current Rank'] = row['Current Rank']
        processed_df.loc[processed_df['Discord Username'] == row['Discord Username'], 'Stated Peak Rank'] = row['Peak Rank']

    return processed_df
