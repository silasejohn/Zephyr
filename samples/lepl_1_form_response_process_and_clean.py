
# global imports
import pandas as pd
import os, sys

# local imports
from __init__ import update_sys_path
update_sys_path()

# unique print inports
from modules.utils.color_utils import warning_print, error_print, info_print, success_print
from modules.scrapers.opgg_scraper import OPGGScraper
from modules.scrapers.league_of_graph_scraper import LeagueOfGraphsScraper

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
        df = pd.DataFrame(columns=['Discord Username', 'Player Riot ID', 'Team Name', 'Rank Diff Score', 'Point Value', 'Stated Player Pos', 'True Player Pos', 'Stated Current Rank', 'Stated Peak Rank', 'True Peak Rank', 'Current Ego Rank', 'S2024 S3 Peak', 'S2024 S2 Peak', 'S2024 S1 Peak', 'S2023 S2 Peak', 'S2023 S1 Peak', 'Player PUUID', 'Player Encrypted Summoner ID', 'Player Encrypted Account ID'], dtype=object)
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
                # warning_print(f'Discord Username {discord_username} already exists in the processed_df dataframe.') 
                pass
        
        success_print('Discord Username column processed successfully.')
        return processed_df
    else:
        # if the column does not exist, log error message
        error_print(f'Column Discord Username does not exist in the form_response_df dataframe.')
        sys.exit(1)

def process_lepl_player_riot_id(form_response_df, processed_df, stage_1_output_file, OPGG_SCRAPE):
    
    if not OPGG_SCRAPE:
        warning_print('OPGG_SCRAPE is set to False. Skipping OPGG scraping.')
        return processed_df
    
    OPGGScraper.set_up_opgg()

    # get slice of 'Discord Username' and 'Player OP.GG' columns
    form_response_df = form_response_df.copy()
    form_response_df = form_response_df[['Discord Username', 'Player OP.GG']]

    # counter = 1
    startProcess = False
    for index, row in form_response_df.iterrows():

        # if in processed_df, the corresponding discord username doesn't have a player riot id, then start processing
        if row['Discord Username'] in processed_df['Discord Username'].values:
            if pd.isnull(processed_df.loc[processed_df['Discord Username'] == row['Discord Username'], 'Player Riot ID'].values[0]):
                startProcess = True

        if not startProcess:
            startProcess = False
            continue
        

        info_print(f"Querying OP.GG for {row['Player OP.GG']}")
        if pd.isnull(row['Player OP.GG']):
            # warning_print(f"Player OP.GG is null for {row['Discord Username']}. Enter OP.GG.")
            # input_opgg = input(f"Enter OP.GG for {row['Discord Username']}: ")
            # if input_opgg == "":
            warning_print(f"OP.GG is empty for {row['Discord Username']}. Skipping.")
            startProcess = False
            continue
        else:
            search_results = OPGGScraper.query_summoner_stats(row['Player OP.GG'])

        # if search results is -1, then continue to the next row
        if search_results == -1:
            startProcess = False
            continue

        # if search_results is a list, then join the list with "|"
        if isinstance(search_results, list):
            search_results = '|'.join(search_results)
        
        print(f"Search Results: {search_results}")
        processed_df.loc[processed_df['Discord Username'] == row['Discord Username'], 'Player Riot ID'] = search_results
        export_processed_roster_csv_info(stage_1_output_file, processed_df)

        startProcess = False
    
    OPGGScraper.DRIVER.quit()  # Close the browser
    success_print(f"Driver Quit!")

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

def process_lepl_true_rank(form_response_df, processed_df, stage_1_output_file, LOG_RANK_SCRAPE):
    if not LOG_RANK_SCRAPE:
        warning_print('LOG_RANK_SCRAPE is set to False. Skipping LOG RANK scraping.')
        return processed_df
    
    setup = False
    counter = 1

    startProcess = False; 
    for index, row in processed_df.iterrows():

        # if no valid Riot ID ... skip this player
        if pd.isnull(row['Player Riot ID']) or row['Player Riot ID'] == "":
            warning_print(f"Player Riot ID is null for {row['Discord Username']}. Skipping.")
            continue

        # if in processed_df, the corresponding discord username doesn't have a player riot id, then start processing
        if row['Discord Username'] in processed_df['Discord Username'].values:
            if pd.isnull(processed_df.loc[processed_df['Discord Username'] == row['Discord Username'], 'Current Ego Rank'].values[0]):
                startProcess = True

        if not startProcess:
            continue

        # obtain clean profile data
        profile_ign_data = row['Player Riot ID']

        # make a copy of the entire row to avoid modifying the original row
        # make a copy of the 'row'
        player_profile = row.copy()
        
        ## most important rank information
        player_profile['True Peak Rank'] = ""

        ## current ego season rank
        player_profile['Peak Ego Rank'] = "" ## unsure if we get this??
        player_profile['Current Ego Rank'] = ""

        # individual season ending ranks
        player_profile['S2024 S3 Peak'] = ""
        player_profile['S2024 S2 Peak'] = ""
        player_profile['S2024 S1 Peak'] = ""
        player_profile['S2023 S2 Peak'] = ""
        player_profile['S2023 S1 Peak'] = ""
    
        success_print(f"{profile_ign_data}")
        info_print(f"{player_profile}", header="Player Profile Row")

        # if multiple profiles, split into profile_ign_list
        # if multiple profiles, splice into a profile list
        profile_ign_list = []
        problem_profiles = []
        if "|" in profile_ign_data:
            profile_ign_list = profile_ign_data.split("|")
        else:
            profile_ign_list.append(profile_ign_data)
        profile_ign_list = [ign.strip() for ign in profile_ign_list]

        # setup the LeagueOfGraphs website for scraping as needed
        if not setup:
            LeagueOfGraphsScraper.set_up_rewind_lol()
            status = LeagueOfGraphsScraper.switch_to_dark_mode()
            setup = True

        # iterate through each profile_ign in the list
        # profile_ign_list = ["Haumea#GCS, BioMatrix#Dead"]
        for profile_ign in profile_ign_list:
            status = LeagueOfGraphsScraper.load_player_profile(profile_ign)
            if status == profile_ign:
                problem_profiles.append(profile_ign)
                # store a copy of problem profiles into the output txt file at data/synthesized/problem_profiles.txt
                with open('data/processed/lepl_problem_profiles.txt', 'a') as f:
                    f.write(f"{profile_ign}\n")            
                continue
            info_print(f"Scraping {profile_ign} Current Ego Rank, Wins, Losses, and Winrate")
            current_ego_rank, current_ego_rank_wins, current_ego_rank_losses, current_ego_rank_wr = LeagueOfGraphsScraper.scrape_player_current_rank()

            # if there is no current ego rank, wait for user input then move on
            if current_ego_rank == -1:
                error_print(f"Error accessing player current rank: {profile_ign}", header='ERROR')
                input("Press Enter to Quit...")
                sys.exit()

            # save a copy of the last profile "Current Ego Rank" if needed
            old_current_ego_rank = player_profile['Current Ego Rank']

            # if peak ego rank is not initialized, initialize to current_ego_rank
            if player_profile['Peak Ego Rank'] == "":
                player_profile['Peak Ego Rank'] = old_current_ego_rank
                info_print(f"Created Peak Ego Rank for {profile_ign} to {old_current_ego_rank}")

            # if the current_ego_rank is empty, update the current_ego_rank
            if old_current_ego_rank == "":
                if current_ego_rank == "UNRANKED":
                    player_profile['Current Ego Rank'] = ""
                    player_profile['Peak Ego Rank'] = ""
                    info_print(f"Created Current Ego Rank for {profile_ign} to UNRANKED")
                else:
                    player_profile['Current Ego Rank'] = current_ego_rank
                    player_profile['Peak Ego Rank'] = current_ego_rank
                    info_print(f"Created Current & Peak Ego Rank for {profile_ign} to {current_ego_rank}")
            # if another profile has a current ego rank that is lower, update the current_ego_rank
            elif player_profile['Current Ego Rank'] != current_ego_rank:
                
                if current_ego_rank == "UNRANKED":
                    info_print(f"Kept (EXISTING) Ego Rank ({player_profile['Current Ego Rank']}) of {profile_ign} instead of shifting to UNRANKED")
                else:
                    old_current_ego_rank_value = LeagueOfGraphsScraper.calculate_rank_score(old_current_ego_rank)
                    new_current_ego_rank_value = LeagueOfGraphsScraper.calculate_rank_score(current_ego_rank)
                    peak_ego_rank_value = LeagueOfGraphsScraper.calculate_rank_score(player_profile['Peak Ego Rank'])

                    # update the current_ego_rank if the current_ego_rank_value is higher than the old_current_ego_rank_value
                    if new_current_ego_rank_value > old_current_ego_rank_value:
                        player_profile['Current Ego Rank'] = current_ego_rank
                        success_print(f"Updated Current Ego Rank for {profile_ign} to {current_ego_rank}")
                    else:
                        error_print(f"Current Ego Rank {old_current_ego_rank} for {profile_ign} is already higher than {current_ego_rank}")

                    # update the peak_ego_rank if the current_ego_rank_value is higher than the peak_ego_rank_value
                    if new_current_ego_rank_value > peak_ego_rank_value:
                        player_profile['Peak Ego Rank'] = current_ego_rank
                        success_print(f"Updated Peak Ego Rank for {profile_ign} to {current_ego_rank}")

            warning_print(f"Scraping {profile_ign} Previous Peak Rank, Wins, Losses, and Winrate")
            previous_peak_rank, previous_rank_wins, previous_rank_losses, previous_rank_wr = LeagueOfGraphsScraper.scrape_player_past_peak_ranks()
            
            # if previous_peak_rank is and empty dict 
            if previous_peak_rank == -1: # this signifies that the dict is empty
                error_print(f"[ERROR] Error accessing player past peak ranks: {profile_ign}")
                input("Press Enter to Quit...")
                sys.exit()

            # update split ranks & true peak ranks as needed 
            for key, item in previous_peak_rank.items():
                # print(f"\n{ColorPrint.CYAN}[SPLIT] {ColorPrint.GREEN}{key}{ColorPrint.RESET}")
                # print(f"\t{ColorPrint.YELLOW}[PEAK RANK] {item}{ColorPrint.RESET}")
                item_rank_score = LeagueOfGraphsScraper.calculate_rank_score(item)
                prior_true_peak_rank_value = LeagueOfGraphsScraper.calculate_rank_score(player_profile['True Peak Rank'])
                if item_rank_score > prior_true_peak_rank_value:
                    player_profile['True Peak Rank'] = item
                    info_print(f">>> Updated True Peak Rank to {item}")
                match (key):
                    case ("S13 (Split 1)"):
                        s13_split1_rank_score = LeagueOfGraphsScraper.calculate_rank_score(player_profile['S2023 S1 Peak'])
                        if item_rank_score > s13_split1_rank_score:
                            player_profile['S2023 S1 Peak'] = item
                            info_print(f">>> Updated S2023 S1 Peak to {item}")
                        else:
                            error_print(f"S2023 S1 Peak {player_profile['S2023 S1 Peak']} is already higher than {item}")
                    case ("S13 (Split 2)"):
                        s13_split2_rank_score = LeagueOfGraphsScraper.calculate_rank_score(player_profile['S2023 S2 Peak'])
                        if item_rank_score > s13_split2_rank_score:
                            player_profile['S2023 S2 Peak'] = item
                            info_print(f">>> Updated S2023 S2 Peak to {item}")
                        else:
                            error_print(f"S2023 S2 Peak {player_profile['S2023 S2 Peak']} is already higher than {item}")
                    case ("S14 (Split 1)"):
                        s14_split1_rank_score = LeagueOfGraphsScraper.calculate_rank_score(player_profile['S2024 S1 Peak'])
                        if item_rank_score > s14_split1_rank_score:
                            player_profile['S2024 S1 Peak'] = item
                            info_print(f"\n>>> Updated S2024 S1 Peak to {item}")
                        else:
                            error_print(f"\nS2024 S1 Peak {player_profile['S2024 S1 Peak']} is already higher than {item}")
                    case ("S14 (Split 2)"):
                        s14_split2_rank_score = LeagueOfGraphsScraper.calculate_rank_score(player_profile['S2024 S2 Peak'])
                        if item_rank_score > s14_split2_rank_score:
                            player_profile['S2024 S2 Peak'] = item
                            info_print(f">>> Updated S2024 S2 Peak to {item}")
                        else:
                            error_print(f"S2024 S2 Peak {player_profile['S2024 S2 Peak']} is already higher than {item}")
                    case ("S14 (Split 3)"):
                        s14_split3_rank_score = LeagueOfGraphsScraper.calculate_rank_score(player_profile['S2024 S3 Peak'])
                        if item_rank_score > s14_split3_rank_score:
                            player_profile['S2024 S3 Peak'] = item
                            info_print(f"\n>>> Updated S2024 S3 Peak to {item}")
                        else:
                            error_print(f"\nS2024 S3 Peak {player_profile['S2024 S3 Peak']} is already higher than {item}")

            info_print(f"\n[{profile_ign}]\nPlayer Profile:\n{player_profile}")
            LeagueOfGraphsScraper.buffer()
            LeagueOfGraphsScraper.create_new_tab()
            LeagueOfGraphsScraper.close_previous_tab()

        # print profile_max_output
        success_print(f"\n[{player_profile['Player Riot ID']}]\nPlayer Profile:\n{player_profile}")

        # apply the changes in data we made to player_profile to the processed_roster
        processed_df.loc[index] = player_profile

        # export the processed_df to the output file
        export_processed_roster_csv_info(stage_1_output_file, processed_df)

        # # wait for user input
        # input("Press Enter to continue...")
        counter += 1
        startProcess = False

    # close the browser once all profiles are scraped
    LeagueOfGraphsScraper.close()
    return processed_df