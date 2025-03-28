
# global imports
import pandas as pd
import numpy as np
import os, sys

# local imports
from __init__ import update_sys_path
update_sys_path()

# unique print inports
from modules.utils.color_utils import warning_print, error_print, info_print, success_print

##########################
### LEPL PV Generation ###
##########################

RANK_POINTS = {
    "Iron 4": 45,       "Iron 3": 44,      "Iron 2": 43,       "Iron 1": 42,
    "Bronze 4": 41,     "Bronze 3": 40,    "Bronze 2": 39,     "Bronze 1": 38,
    "Silver 4": 37,     "Silver 3": 36,    "Silver 2": 35,    "Silver 1": 34,
    "Gold 4": 33,      "Gold 3": 32,     "Gold 2": 31,      "Gold 1": 30,
    "Platinum 4": 29,  "Platinum 3": 28, "Platinum 2": 27,  "Platinum 1": 26,
    "Emerald 4": 25,   "Emerald 3": 24,  "Emerald 2": 23,   "Emerald 1": 22,
    "Diamond 4": 21,   "Diamond 3": 20,  "Diamond 2": 19,   "Diamond 1": 18,
    "Master": 17,      "Grandmaster": 11,  "Challenger": 5,
    "Iron": 43.5, "Bronze": 39.5, "Silver": 9.5, "Gold": 31.5, "Platinum": 27.5 # metal rank averages
}

APEX_RANKS = ["Master", "Grandmaster", "Challenger"]

# function to determine most recent split w/ a rank value
def get_most_recent_past_split_rank(row):
    for col in ['S2024 S3 Peak', 'S2024 S2 Peak', 'S2024 S1 Peak', 'S2023 S2 Peak', 'S2023 S1 Peak']:

        if not row[col] or pd.isna(row[col]):
            continue # skip empty or NaN values

        # if the rank is an apex rank, only keep the first term (for RANK_POINTS) then add the 2nd term
        if isinstance(row[col], str) and row[col].split(" ")[0] in APEX_RANKS:
            return (RANK_POINTS.get(row[col].split(" ")[0], -1) - (int(row[col].split(" ")[1]) / 100)) 
        else:
            return RANK_POINTS.get(row[col], -1)
    return -1 # if all columns are empty, return -1

def calculate_avg_rank(row, cols, player_riot_id):    
    # if any of the split ranks contains an apex rank, only keep the first term (for RANK_POINTS) then add the 2nd term
    values = [
        (RANK_POINTS.get(row[col].split(" ")[0], -1) - (int(row[col].split(" ")[1]) / 100)) 
        if isinstance(row[col], str) and row[col].split(" ")[0] in APEX_RANKS 
        else RANK_POINTS.get(row[col], -1)
        for col in cols if pd.notna(row[col])  # Skip NaN values explicitly
    ]

    if values:
        # remove all -1 values from values (not obtained values)
        values = [val for val in values if val != -1]

        # print(f"{row[player_riot_id]} values >>> {values} <<< ")  # Debugging line

        if not values: # if no valid past ranks in this time slice exist
            return -1
 
        return sum(values) / len(values) # return the average of the values
    return -1 # return if all split values are non-existent

def adjust_columns_if_apex_rank(row):
    if row["A"] in APEX_RANKS:
        row["D"] = row["C"]  # Move the old C to D
        row["C"] = row["B"]  # Move B to C
        row["B"] = ""        # Remove B since it's unused in these cases
    return row

def calculate_peak_rank_points(peak_rank):
    if isinstance(peak_rank, str):
        terms = peak_rank.split(" ") 
    else:
        return -1 # if peak_rank is not a string, return -1
    
    if len(terms) == 2:
        return RANK_POINTS.get(terms[0] + " " + terms[1])
    elif len(terms) == 3:
        # Handle the case where the rank is "Master 0 LP"
        if terms[0] in APEX_RANKS:
            return RANK_POINTS.get(terms[0]) - (int(terms[1]) / 100)
        else:
            error_print(f"Unexpected apex_rank format (apex rank): {peak_rank}")
            return -1
    else:
        error_print(f"Unexpected peak rank format (regular rank): {peak_rank}")
        return -1 # if peak_rank is not in the expected format, return -1
    
def calculate_point_value(row, cols):
    values = [row[col] for col in cols]  # obtain values from columns
    filtered_values = [v for v in values if v != -1 and not pd.isna(v)] # skip -1 and NaN values
    
    # return the average of the values or -1
    return np.mean(filtered_values) if filtered_values else -1

def generate_lepl_rank_points_stats(processed_df, stage_3_output_file):

    # make copy of the processed dataframe
    finalized_df = processed_df.copy()

    # add columns for "current_season_rank_points", "peak_rank_points" to finalized_df

    # split a column by spaces only if there is a value in the column, else return NaN
    finalized_df["A"] = finalized_df["Current Ego Rank"].str.split(" ", n=1, expand=True)[0]
    finalized_df["trash"] = finalized_df["Current Ego Rank"].str.split(" ", n=1, expand=True)[1]
    finalized_df["B"] = finalized_df["trash"].str.split(" ", n=1, expand=True)[0]
    finalized_df["trash"] = finalized_df["trash"].str.split(" ", n=1, expand=True)[1]
    finalized_df["C"] = finalized_df["trash"].str.split(" ", n=1, expand=True)[0]
    finalized_df["trash"] = finalized_df["trash"].str.split(" ", n=1, expand=True)[1]
    finalized_df["D"] = finalized_df["trash"].str.split(" ", n=1, expand=True)[0]

    # adjust columns if the rank is an apex rank
    finalized_df = finalized_df.apply(adjust_columns_if_apex_rank, axis=1)

    # combine A and B
    finalized_df["Current Ego Rank Tier"] = finalized_df["A"] + " " + finalized_df["B"]
    finalized_df["Current Ego Rank LP"] = finalized_df["C"] + " " + finalized_df["D"]

    # Calculate current_season_rank_points
    finalized_df["Current Ego Rank Tier Points"] = finalized_df["Current Ego Rank Tier"].str.strip().map(RANK_POINTS)
    finalized_df["Current Ego Rank LP (float)"] = finalized_df["Current Ego Rank LP"].str.replace("LP", "").str.strip().replace(" ", "")
    finalized_df["Current Ego Rank LP (float) Points"] = (finalized_df["Current Ego Rank LP (float)"].astype(float) / 100).round(2)
    finalized_df["current_season_rank_points"] = finalized_df["Current Ego Rank Tier Points"] - finalized_df["Current Ego Rank LP (float) Points"]

    # Calculate peak_rank_points
    finalized_df["peak_rank_points"] = finalized_df["True Peak Rank"].apply(calculate_peak_rank_points)
    
    
    # add a column header (with no data) for "prev_split_rank_points", "past_year_avg_rank_points", "past_2_years_avg_rank_points" to finalized_df
    finalized_df["prev_split_rank_points"] = finalized_df["current_season_rank_points"].copy()
    finalized_df["prev_split_rank_points"] = finalized_df["prev_split_rank_points"].fillna(0)
    finalized_df["prev_split_rank_points"] = finalized_df["prev_split_rank_points"].astype(float)

    finalized_df["past_year_avg_rank_points"] = finalized_df["current_season_rank_points"].copy()
    finalized_df["past_year_avg_rank_points"] = finalized_df["past_year_avg_rank_points"].fillna(0)
    finalized_df["past_year_avg_rank_points"] = finalized_df["past_year_avg_rank_points"].astype(float)

    finalized_df["past_2_years_avg_rank_points"] = finalized_df["current_season_rank_points"].copy()
    finalized_df["past_2_years_avg_rank_points"] = finalized_df["past_2_years_avg_rank_points"].fillna(0)
    finalized_df["past_2_years_avg_rank_points"] = finalized_df["past_2_years_avg_rank_points"].astype(float)

    # for 'prev_split_rank_points'
    finalized_df["prev_split_rank_points"] = finalized_df.apply(get_most_recent_past_split_rank, axis=1)

    # for 'past_year_avg_rank_points'
    finalized_df["past_year_avg_rank_points"] = finalized_df.apply(lambda row: calculate_avg_rank(row, ['S2024 S3 Peak', 'S2024 S2 Peak', 'S2024 S1 Peak'], 'Player Riot ID'), axis=1)

    # for 'past_2_years_avg_rank_points'
    finalized_df["past_2_years_avg_rank_points"] = finalized_df.apply(lambda row: calculate_avg_rank(row, ['S2024 S3 Peak', 'S2024 S2 Peak', 'S2024 S1 Peak', 'S2023 S2 Peak', 'S2023 S1 Peak'], 'Player Riot ID'), axis=1)

    # round all rank points columns to 2 decimal places
    finalized_df["current_season_rank_points"] = finalized_df["current_season_rank_points"].round(2)
    finalized_df["peak_rank_points"] = finalized_df["peak_rank_points"].round(2)
    finalized_df["prev_split_rank_points"] = finalized_df["prev_split_rank_points"].round(2)
    finalized_df["past_year_avg_rank_points"] = finalized_df["past_year_avg_rank_points"].round(2)
    finalized_df["past_2_years_avg_rank_points"] = finalized_df["past_2_years_avg_rank_points"].round(2)

    # eliminate unneeded columns 
    finalized_df = finalized_df.drop(columns=["A", "B", "C", "D", "trash"])
    finalized_df = finalized_df.drop(columns=["Current Ego Rank LP (float) Points", "Current Ego Rank LP (float)", "Current Ego Rank Tier Points", "Current Ego Rank LP", "Current Ego Rank Tier"])
    
    # calculate "point value" of each plaeyr
    finalized_df.replace('', np.nan, inplace=True) # replace all empty strings with NaN
    finalized_df["Point Value"] = finalized_df.apply(
        lambda row: calculate_point_value(row, ['current_season_rank_points', 'peak_rank_points', 'prev_split_rank_points', 'past_year_avg_rank_points', 'past_2_years_avg_rank_points']), axis=1
    )

    # return the finalized dataframe
    processed_df = finalized_df.copy()

    return processed_df
    








    return processed_df