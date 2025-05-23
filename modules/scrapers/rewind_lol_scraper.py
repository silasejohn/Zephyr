##########################
### Import Statements ####
##########################

# local imports
from __init__ import update_sys_path
update_sys_path()

# data manipulation, time buffering, quick exit, csv editing
import pandas as pd
import time, sys, csv, os

# pretty printing and color
import modules.utils.color_utils as ColorPrint
from modules.utils.file_utils import load_json_from_file

# Selenium WebDriver Options
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions    #  for FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions      # for ChromeOptions
from selenium.webdriver.firefox.service import Service                      # for FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService      # for ChromeService
from selenium.webdriver.common.by import By                                 # for locating elements BY specific types (e.g. ID, NAME, etc.)
from selenium.webdriver.common.keys import Keys                             # for clicking RETURN
from selenium.webdriver.support.ui import Select                            # for dropdown menus (element selection)
from selenium.webdriver.support.ui import WebDriverWait                     # for waiting for elements to load
from selenium.webdriver.support import expected_conditions as EC            # for expected conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException     # for timeout exceptions

def zephyr_print(msg):
    print(f"\n[[{ColorPrint.MAGENTA} Z E P H Y R {ColorPrint.RESET}]] >> {msg}...")

def create_data_df(csv_file):
    data_df = pd.read_csv(csv_file)
    return data_df

#######################################
### LeagueChampScraper (rewind.lol) ###
#######################################
class LeagueChampScraper:

    MAIN_WEBSITE = 'https://rewind.lol/'
    DRIVER = None
    BROWSER = "chrome"
    WEBSITE_TIMEOUT = 5
    POSITION_LIST = ["top", "jng", "mid", "bot", "sup"]

    @staticmethod
    def input(inputType: str = None):
        if inputType == "player_ign":
            print("Enter the Player IGN: ")
            player_ign = input()
            return player_ign
        else:
            # default case
            print("Enter the Player IGN: ")
            player_ign = input()
            return player_ign
        
    @staticmethod
    # sets up the rewind.lol website
    def set_up_rewind_lol():
        try: 
            zephyr_print("Prepping Rewind.lol")
            LeagueChampScraper.get_web_driver()
            LeagueChampScraper.DRIVER.get(LeagueChampScraper.MAIN_WEBSITE)
            return 1 # success
        except Exception as e:
            print(f"Error: {e}")
            LeagueChampScraper.close()
            return -1 # error
        
    @staticmethod
    # enter in player IGN and arrive at their rewind.lol profile page
    def load_player_profile(player_ign):
        zephyr_print(f"Entering Player IGN: {player_ign}")
        try:
            status = LeagueChampScraper.select_region()

            # Find the rewind.lol search box, enter player IGN, and hit Enter
            search_box = LeagueChampScraper.DRIVER.find_element(By.CLASS_NAME, 'main__interface-menu-input')
            search_box.send_keys(player_ign + Keys.RETURN)  # Send query and hit Enter

            return 1 # success
        except Exception as e:
            print(f"Error: {e}")
            return -1 # error
    
    @staticmethod
    # waits for an "element" to show up on page
    # used to wait for page (and specific element) to load
    def wait_for_element_to_load(by, value, timeout=10, custom_error_msg=None):
        try:
            element = WebDriverWait(LeagueChampScraper.DRIVER, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            if custom_error_msg:
                print(f"{ColorPrint.RED}{custom_error_msg}{ColorPrint.RESET}")
            else:
                print(f"{ColorPrint.RED}{value} Element not Found!{ColorPrint.RESET}")
            return -1
    
    @staticmethod
    # access player's champion history
    def access_player_champion_history():
        print(f"{ColorPrint.YELLOW}>> Accessing Player Champion History{ColorPrint.RESET}")
        try:
            # Find the Champion History Button and Click
            champ_history_menu = LeagueChampScraper.DRIVER.find_element(By.XPATH, "//a[contains(@onclick, '/user_champions.html')]")
            champ_history_menu.click()  # Click the element

        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error accessing player champion history: {e}{ColorPrint.RESET}")

    @staticmethod
    # access player champion history table
    def access_player_champion_history_table(player_ign, file_name):
        print(f"{ColorPrint.YELLOW}>> Accessing Player Champion History Table{ColorPrint.RESET}")
        try:
            # role_prio_list = [] # initialize list for storing role priority entries

            # Test: Find the Champion History Table
            LeagueChampScraper.wait_for_element_to_load(By.XPATH, "//*[text()='Champions Played and stats for PvP games']")
            champ_history_header = LeagueChampScraper.DRIVER.find_element(By.XPATH, "//*[text()='Champions Played and stats for PvP games']")

            # Find a title element from header row
            LeagueChampScraper.wait_for_element_to_load(By.XPATH, "//th[contains(@title, 'total KDA')]")
            element = LeagueChampScraper.DRIVER.find_element(By.XPATH, "//th[contains(@title, 'total KDA')]")

            # Find Header Row
            header_row = element.find_element(By.XPATH, "parent::*")
            # print(f"{ColorPrint.YELLOW}Header: {header_row.text}{ColorPrint.RESET}")

            # Find Main Table of Data
            champ_history_table_tbody = header_row.find_element(By.XPATH, "parent::*")

            # store all the <tr> rows in this tbdoy element champ_history_table_tbody
            tr_elements = champ_history_table_tbody.find_elements(By.TAG_NAME, 'tr')

            # Extract Header Row from Table
            header_row = tr_elements[0].find_elements(By.TAG_NAME, 'th')
            # print(f"{ColorPrint.YELLOW}# of Headers: {len(header_row)}{ColorPrint.RESET}")

            # Extract Data Rows from Table
            data_rows = tr_elements[1:]

            # Write to CSV File
            role_prio_entry = []
            with open(file_name, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if header_row: # write headers
                    writer.writerow([header.text.strip().replace("\n"," ") for header in header_row])
                else: # If there are no 'th' tags, use the first row as headers
                    first_row = data_rows[0].find_elements(By.TAG_NAME, 'td')
                    writer.writerow([cell.text for cell in first_row])

                for row in data_rows: # Write the rows to the CSV file (each tr is a row)
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    
                    if cells:  # Skip rows without 'td' elements
                        row_data = []
                        
                        first_cell = True
                        for cell in cells:
                            if first_cell:
                                try:
                                    img_src_text = cells[0].find_element(By.TAG_NAME, 'span').find_element(By.TAG_NAME, 'img').get_attribute('src')
                                    role = img_src_text.split('/')[-1].split('.webp')[0]
                                    # print(f"{ColorPrint.YELLOW}Position: {role}{ColorPrint.RESET}")
                                    new_cell_text = cells[0].text + f" ({role})"
                                    row_data.append(new_cell_text.strip())
                                except NoSuchElementException:
                                    # if the text has a "_" in it, then it is a champion name
                                    if "_" in cells[0].text:
                                        new_cell_text = cells[0].text.replace("_", "[Role] ").strip()
                                        role_prio_entry.append(cells[0].text.replace("_", "").strip())
                                        row_data.append(new_cell_text)
                                    else:
                                        row_data.append(cells[0].text.strip())
                                first_cell = False
                            else:
                                row_data.append(cell.text.strip())
                        writer.writerow(row_data)
                role_prio_msg = f"Player Role Priorities (past 2 years): {role_prio_entry}"
                print(f"{ColorPrint.GREEN}{role_prio_msg}{ColorPrint.RESET}")

            # import the csv back into a dataframe
            print(f"{ColorPrint.YELLOW}>> Refining CSV File: {file_name}{ColorPrint.RESET}")
            champ_df = pd.read_csv(file_name, sep=',')

            # loop through each row in the dataframe
            print(f"{ColorPrint.YELLOW}>> Extracting Roles from Champion Names{ColorPrint.RESET}")
            for index, row in champ_df.iterrows():
                champ_name = row['champion']
                # if the champ_name has [Role] in it, output 'Overview' in the 'Role' column
                # print(f"{ColorPrint.YELLOW}Champion: {champ_name}{ColorPrint.RESET}")
                if champ_name.find("[Role]") != -1:
                    champ_df.at[index, 'role'] = "OVERVIEW"
                # if the champ_name has parenthesis in it, extract the role from the parenthesis into the 'Role' column
                elif champ_name.find("(") != -1:
                    champ_df.at[index, 'role'] = champ_name.split("(")[1].split(")")[0]
                else: # if the champ_name is a champion name, extract the role from the CHAMPS_IN_ROLES dictionary
                    # champ_df.at[index, 'role'] = LeagueChampScraper.CHAMPS_IN_ROLES[champ_name]
                    pass
            file_name = file_name.replace("_raw.csv", "") # strip .csv from file_name
            file_name = file_name + "_refined.csv" # add "_refined.csv" to file_name
            champ_df.to_csv(file_name, index=False) # save to new csv file

            ### Role by Role df ### 
            # for each role of [top, jng, mid, bot, sup, OVERVIEW], create a new df and save to csv
            for role in ['top', 'jng', 'mid', 'bot', 'sup', 'OVERVIEW', '']:
                role_df = champ_df[champ_df['role'] == role]
                if not role_df.empty:
                    if role == '':
                        role_df.to_csv(file_name.replace("_refined.csv", f"_leftovers.csv"), index=False)
                    elif role == 'OVERVIEW':
                        role_df.to_csv(file_name.replace("_refined.csv", f"_role_distribution.csv"), index=False)
                    else:
                        role_df.to_csv(file_name.replace("_refined.csv", f"_{role}.csv"), index=False)
            # return role_prio_list
        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error accessing player champion history table: {e}{ColorPrint.RESET}")
            input("Press Enter to Continue...")
            # return role_prio_list

    @staticmethod
    # access player's champion history for a single champion
    def access_single_champion_history(player_name, champion_name):

        # make champion_name CamelCase
        champion_name = champion_name.lower().title()

        zephyr_print(f"Accessing Player Champion History for <{champion_name}>")
        try:
            # Find the Champion History Button and Click
            champ_select_element = LeagueChampScraper.DRIVER.find_element(By.ID, 'd1f-champion-name')

            # Click the element
            champ_select_element.click()

            # Wrap the element in a Select object
            champ_select = Select(champ_select_element)

            # Select an option by value (e.g., 'NA' for North America)
            # 3 options: select_by_index, select_by_value, select_by_visible_text
            champ_select.select_by_visible_text(champion_name)

            # click
            champ_select_element.click()

            return 1 # success

        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error accessing player champion history for {champion_name}: {e}{ColorPrint.RESET}")
            return -1 # error

    @staticmethod
    # selection of region NA
    def select_region(region = 'NA'):
        print(f"{ColorPrint.YELLOW}>> Selecting Region: {region}{ColorPrint.RESET}")
        try:
            # Find the Region Select Dropdown
            region_select_element = LeagueChampScraper.DRIVER.find_element(By.CLASS_NAME, 'main__interface-menu-input-servers')

            # Wrap the element in a Select object
            region_select = Select(region_select_element)

            # Select an option by value (e.g., 'NA' for North America)
            region_select.select_by_value('NA')
            
            return 1 # success
        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error selecting region {region}: {e}{ColorPrint.RESET}")
            return -1 # error

    @staticmethod
    # sets up the webdriver (automated chrome access)
    # [returns] 1 if driver created, 0 if driver already exists
    def get_web_driver():
        if LeagueChampScraper.DRIVER is None:
            zephyr_print("Setting up Chrome WebDriver")
            if LeagueChampScraper.BROWSER.lower() == "firefox":
                options = FirefoxOptions()
                options.headless = True  # Runs in headless mode, no UI.
                service = Service('/path/to/geckodriver')  # Path to geckodriver
                LeagueChampScraper.DRIVER = webdriver.Firefox(service=service, options=options)
            elif LeagueChampScraper.BROWSER.lower() == "chrome":
                options = ChromeOptions()
                options.headless = True  # Runs in headless mode, no UI.
                service = ChromeService('/opt/homebrew/bin/chromedriver')  # Path to chromedriver
                LeagueChampScraper.DRIVER = webdriver.Chrome(service=service, options=options)
            else:
                raise ValueError("Only 'firefox' and 'chrome' browsers are supported.")
            return 1 # driver created
        else:
            return 0 # driver already exists

    def buffer(time_sec = WEBSITE_TIMEOUT):
        time.sleep(time_sec)

    @staticmethod
    def close():
        LeagueChampScraper.DRIVER.quit()

    @staticmethod   
    def close_previous_tab():
        # Get a list of all open tabs
        tabs = LeagueChampScraper.DRIVER.window_handles

        # Switch to the previous tab
        LeagueChampScraper.DRIVER.switch_to.window(tabs[0])

        # Close the Current Tab
        LeagueChampScraper.DRIVER.close()

        # Switch to the previous tab open
        LeagueChampScraper.DRIVER.switch_to.window(tabs[-1]) # tabs[-1] is the last tab opened 

    @staticmethod
    def create_new_tab():
        # # Open a new tab
        # LeagueChampScraper.DRIVER.execute_script("window.open('');")

        # # Switch to the new tab
        # LeagueChampScraper.DRIVER.switch_to.window(LeagueChampScraper.DRIVER.window_handles[-1])

        # Load a new instance of rewind.lol in new tab
        LeagueChampScraper.DRIVER.execute_script("window.open('https://rewind.lol', '_blank');")

    @staticmethod
    # update team champion history
    def update_team_champ_history(tournament_id: str, team_id: str, player_riot_ids: list[str], run_update: bool = False):
            
        # setup the rewind.lol website for scraping
        LeagueChampScraper.set_up_rewind_lol()

        profiles_to_update = []

        for player_account in player_riot_ids:
            print(f"{ColorPrint.YELLOW}[Cleaning Player Account] {player_account}{ColorPrint.RESET}")

            # skip empty rows / invalid IGNs
            if player_account == "":
                continue 

            # if player_account is a string, convert to list                
            if type(player_account) == str:
                player_account = [player_account]
            
            # if there is only one account, add to list
            if len(player_account) == 1:
                if '#' not in player_account[0]:
                    print(f"{ColorPrint.RED}Error: Invalid Player IGN of {player_account}{ColorPrint.RESET}")
                    continue
                profiles_to_update.append(player_account[0])

            # if there are multiple accounts, add each account to list
            elif len(player_account) > 1:
                for account in player_account:
                    if '#' not in account:
                        print(f"{ColorPrint.RED}Error: Invalid Player IGN of {player_account}{ColorPrint.RESET}")
                        continue 
                    profiles_to_update.append(account)

        for profile in profiles_to_update:

            zephyr_print(f"{ColorPrint.RED}Updating Player Champion History for {profile}{ColorPrint.RESET}")

            # access updated player champion history table + store into csv
            LeagueChampScraper.load_player_profile(profile)
            LeagueChampScraper.access_player_champion_history()

            # create directory {team_id} if it doesn't exist
            if not os.path.exists(f"data/processed/champ_mastery/{tournament_id}/{team_id}"):
                os.makedirs(f"data/processed/champ_mastery/{tournament_id}/{team_id}")

            # output csv file
            champ_history_output = f"data/processed/champ_mastery/{tournament_id}/{team_id}/{profile}_raw.csv"

            LeagueChampScraper.access_player_champion_history_table(profile, champ_history_output)

            zephyr_print(f"{ColorPrint.GREEN}Player Champion History for {profile} UPDATED{ColorPrint.RESET}")

            # buffer and close tab, then create new tab
            LeagueChampScraper.buffer()
            LeagueChampScraper.create_new_tab()
            LeagueChampScraper.close_previous_tab()
        
        print(f"{ColorPrint.GREEN}Finished Updating Team Champion History{ColorPrint.RESET}")
    
        LeagueChampScraper.close()

    @staticmethod
    # access team roster information
    def retrieve_team_roster(team_id: str):
        team_roster_riot_ids = []
        team_roster_positions = []
        input_json_file = f"constants/teams/{team_id}.json"
        
        # if file doesn't exist or is empty return
        if not os.path.exists(input_json_file) or os.stat(input_json_file).st_size == 0:
            print(f"{ColorPrint.RED}Error: Team JSON File Not Found{ColorPrint.RESET}")
            return -1
        
        # load the json file 
        team_data = load_json_from_file(input_json_file)

        # ensure that team_id matches the json roster
        if team_data['team_id'] != team_id:
            print(f"{ColorPrint.RED}Error: Team ID Mismatch{ColorPrint.RESET}")
            return -1, -1
        
        zephyr_print(f"Retrieving Team Roster Information for Team ID: {team_id}")

        # get the roster information
        team_roster = team_data['rosters']

        for player in team_roster:
            player_accounts = player['player_riot_id']
            if len(player_accounts) == 1:
                team_roster_riot_ids.append(player_accounts[0])
            elif len(player_accounts) > 1:
                player_account_list = []
                for account in player_accounts:
                    player_account_list.append(account)
                team_roster_riot_ids.append(player_account_list)
            else:
                print(f"{ColorPrint.RED}Error: No Player Accounts Found{ColorPrint.RESET}")

            # get the positions information
            player_positions = player['player_pos']
            
            # split by "|" to get multiple positions
            pos_list = player_positions.split("|")
            pos_list = [pos.lower() for pos in pos_list]
            
            if "captain" in pos_list:
                pos_list.remove("captain")

            if "jgl" in pos_list:
                pos_list[pos_list.index("jgl")] = "jng"

            team_roster_positions.append(pos_list)

        print(f"\n----------------")
        print(f"{ColorPrint.CYAN}[{team_id} ROSTER]{ColorPrint.RESET}")
        print(f"----------------")
        for player_riot_id in team_roster_riot_ids:
            print(f"{ColorPrint.GREEN}{player_riot_id}{ColorPrint.RESET}")
            print(f"{ColorPrint.YELLOW}{team_roster_positions[team_roster_riot_ids.index(player_riot_id)]}{ColorPrint.RESET}\n")

        input("Press Enter to Continue...")

        return team_roster_riot_ids, team_roster_positions
    
    @staticmethod
    def weighted_average(series, weights):
        return (series * weights).sum() / weights.sum()

    @staticmethod
    # output player (multi account) champion mastery (in last 2 years)
    def access_player_champ_pool(tournament_id, team_id, player_accounts, pos):

        # set up empty df for storing player champ pool
        player_champ_pool_df = pd.DataFrame()

        # if player_account is not a list (is a string) then convert to list
        if type(player_accounts) == str:
            player_accounts = [player_accounts]
        
        zephyr_print(f"Accessing Player Champion Pool for {player_accounts[0]} in {pos}")
        potential_accounts_for_combining = player_accounts.copy()

        # create empty df for storing combined role stats for each player account
        role_dist_df = pd.read_csv(f"data/processed/champ_mastery/{tournament_id}/{team_id}/{player_accounts[0]}_role_distribution.csv")
        # drop columns "average game duration", "role"
        role_dist_df = role_dist_df.drop(columns=["average game duration", "role", "triple kills", "quadra kills", "penta kills", "per game K / D / A", "total KD", "average KD", "average KDA ±SD", "total KDA"])
        role_dist_flag = False


        for player_ign in player_accounts:
            
            # simple boolean flag to only df concentate if not the first player in player_accounts
            if role_dist_flag:
                file = f"data/processed/champ_mastery/{tournament_id}/{team_id}/{player_ign}_role_distribution.csv"
                new_role_dist_df = pd.read_csv(file)
                new_role_dist_df = new_role_dist_df.drop(columns=["average game duration", "role", "triple kills", "quadra kills", "penta kills", "per game K / D / A", "total KD", "average KD", "average KDA ±SD", "total KDA"])
                role_dist_df = pd.concat([role_dist_df, new_role_dist_df], axis=0) # append contents of file to role_dist_df
            else: 
                role_dist_flag = True

            does_file_exist = False
            for file in os.listdir(f"data/processed/champ_mastery/{tournament_id}/{team_id}"):
                if file.startswith(player_ign) and file.endswith(pos + ".csv"):
                    print(f">> {ColorPrint.YELLOW}Processing {player_ign} champ pool for {pos}{ColorPrint.RESET}")
                    player_account_champ_pool_df = pd.read_csv(f"data/processed/champ_mastery/{tournament_id}/{team_id}/" + file)
                    player_champ_pool_df = pd.concat([player_champ_pool_df, player_account_champ_pool_df], axis=0)
                    does_file_exist = True
                    break
            if not does_file_exist:
                filepath = f"data/processed/champ_mastery/{tournament_id}/{team_id}/problem_profiles.txt"
                problem_text = "[" + team_id + "] - " + player_ign + " " + pos + "\n"

                # check if file exists, append if it does 
                if os.path.exists(filepath):
                    with open(filepath, 'a') as f:
                        f.write(problem_text)
                else:
                    with open(filepath, 'w') as f:
                        f.write(problem_text)
                
                print(f"{ColorPrint.RED}Error: File Not Found for Team {team_id} in Tournament {tournament_id} and player account {player_ign} in role {pos}{ColorPrint.RESET}")
                potential_accounts_for_combining.remove(player_ign)
        
        """ combine role distribution stats for each player account """
        # strip % from winrate, average KP, first blood rate
        for col in ["winrate", "average KP", "first blood rate"]:
            role_dist_df[col] = role_dist_df[col].str.rstrip('%').astype(float)

        # groupby similar rows with unique aggregation
        aggregated_role_df = role_dist_df.groupby("champion").apply(lambda group: pd.Series({
            "total games": group["total games"].sum(),
            "wins": group["wins"].sum(),
            "losses": group["losses"].sum(),
            "average KP": LeagueChampScraper.weighted_average(group["average KP"], group["total games"]),
            "first blood rate": LeagueChampScraper.weighted_average(group["first blood rate"], group["total games"]),
        })).reset_index()

        # calculate winrate again based on aggregated wins/games
        aggregated_role_df["winrate"] = (aggregated_role_df["wins"] / aggregated_role_df["total games"]) * 100

        # format percentage columns
        for col in ["winrate", "average KP", "first blood rate"]:
            aggregated_role_df[col] = aggregated_role_df[col].map(lambda x: f"{x:.2f}%")

        # change "total games", "wins", "losses" to int
        aggregated_role_df["total games"] = aggregated_role_df["total games"].astype(int)

        # replace "[Role]" with player_ign[0] in "champion" column
        player_ign = player_accounts[0].split("#")[0]
        aggregated_role_df["champion"] = aggregated_role_df["champion"].str.replace("[Role]", f"[{player_ign}]")

        # output aggregate role distribution stats 
        print(f"{ColorPrint.YELLOW}>> Aggregated Role Distribution Stats for {player_accounts} in {pos}{ColorPrint.RESET}")
        print (aggregated_role_df)

        # save to team_id role distribution csv (check if file exists first)
        file_path = f"data/processed/champ_mastery/{tournament_id}/{team_id}/{team_id}_role_distribution.csv"
        if os.path.exists(file_path):
            # append to existing file
            aggregated_role_df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            # create new file
            aggregated_role_df.to_csv(file_path, index=False)

        # before printing the df, combine the stats for each player account
        if len(potential_accounts_for_combining) > 1:
            player_champ_pool_df = LeagueChampScraper.combine_champ_stats(player_champ_pool_df, potential_accounts_for_combining, pos)
        elif len(potential_accounts_for_combining) == 1:
            print(f"{ColorPrint.RED}>> [Single Account] No Need to Combine Champion Stats for {potential_accounts_for_combining[0]} in {pos}!{ColorPrint.RESET}")
        else:
            print(f"{ColorPrint.RED}Error: In {pos} position... No Player Accounts {player_accounts} Found for {team_id} in {tournament_id}{ColorPrint.RESET}")
            input("Press Enter to Continue...")
            return

        # print the df but combined stats
        print(f"{ColorPrint.GREEN}[{pos}] <{player_accounts}> Combined Champion Stats{ColorPrint.RESET}")

        # drop columns 'triple kills', 'quadra kills', 'penta kills', 'role', 'average game duration'
        sorted_player_champ_pool_df = player_champ_pool_df.sort_values(by='total games', ascending=False)
        partial_player_champ_pool_df = sorted_player_champ_pool_df.drop(columns=['triple kills', 'quadra kills', 'penta kills', 'role', 'average game duration', 'per game K / D / A', 'total KD', 'average KD', 'average KDA ±SD', 'total KDA'])
        print(partial_player_champ_pool_df)
        # sort by 'total games' in descending order
        input("Press Enter to Continue...")

    @staticmethod
    def access_team_champ_pool(tournament_id: str, team_id: str, team_roster, team_pos_list):
        # empty the team role dist file if it exists
        file_path = f"data/processed/champ_mastery/{tournament_id}/{team_id}/{team_id}_role_distribution.csv"
        if os.path.exists(file_path):
            # remove the file
            os.remove(file_path)
            print(f"{ColorPrint.YELLOW}>> Removed Existing Team Role Distribution File: {file_path}{ColorPrint.RESET}")
        else:
            print(f"{ColorPrint.YELLOW}>> No Existing Team Role Distribution File Found: {file_path}{ColorPrint.RESET}")

        # input user wait
        input("Press Enter to Continue...")

        position_list = ["top", "jng", "mid", "bot", "sup"]
        zephyr_print(f"Accessing Team Champion Pool for Team ID [{team_id}] from [{tournament_id}]")
        for role in position_list:
            for i in range(len(team_roster)):
                if role in team_pos_list[i]:
                # pos_list = team_pos_list[i] # get the positions for the player / player accounts
                # for pos in pos_list:
                    zephyr_print(f"Pulling champ pool for {team_roster[i]} in {role}")
                    LeagueChampScraper.access_player_champ_pool(tournament_id, team_id, team_roster[i], role)
        
        # sort the team wide role distribution pool by "total games" in descending order
        team_role_dist_df = pd.read_csv(f"data/processed/champ_mastery/{tournament_id}/{team_id}/{team_id}_role_distribution.csv")
        # eliminate duplicate rows
        team_role_dist_df = team_role_dist_df.drop_duplicates(subset=['champion'], keep='first')
        team_role_dist_df = team_role_dist_df.sort_values(by='total games', ascending=False)
        print(f"{ColorPrint.YELLOW}>> Team Role Distribution Stats for {team_id} in {tournament_id}{ColorPrint.RESET}")
        print(team_role_dist_df)

        # store the team role distribution stats in a csv file
        team_role_dist_df.to_csv(f"data/processed/champ_mastery/{tournament_id}/{team_id}/{team_id}_role_distribution.csv", index=False)
        

    @staticmethod
    # combine appropriate stats for the champ df per each player account
    def combine_champ_stats(player_champ_pool_df, player_accounts, pos):
        champ_pool_was_combined = False
        in_depth_print = True

        print(f"{ColorPrint.YELLOW}>> Attempting to Combine Champion Stats for {player_accounts} in {pos}{ColorPrint.RESET}")

        # create a new df w/ same columns as player_champ_pool_df
        updated_player_champ_pool_df = pd.DataFrame(columns=player_champ_pool_df.columns)
        
        # loop through each unique champion in the player_champ_pool_df
        for champ_name in player_champ_pool_df['champion'].unique():

            # identify the slice of the df containing rows with the same champ_name (make a copy)
            champ_df = player_champ_pool_df[player_champ_pool_df['champion'] == champ_name].copy()

            # skip if there is only one row (means only one account)
            if len(champ_df) == 1:
                if updated_player_champ_pool_df.empty:
                    updated_player_champ_pool_df = champ_df
                else:
                    updated_player_champ_pool_df = pd.concat([updated_player_champ_pool_df, champ_df], axis=0)
                continue
            elif len(champ_df) < 1:
                print(f"{ColorPrint.RED}Error: No Champion Data Found for {champ_name}{ColorPrint.RESET}")
                return -1

            # print the champ_df slice if there are multiple rows
            print(champ_df)
            champ_pool_was_combined = True

            # MetaVariables Storing Contribution Values for each Player (index = account_num)
            account_num = 0
            total_games_per_account = [] * len(champ_df)
            total_wins_per_account = [] * len(champ_df)
            total_losses_per_account = [] * len(champ_df)
            contributing_total_KDA_per_account = [] * len(champ_df)
            contributing_average_KDA_per_account = [] * len(champ_df)
            contributing_average_KDA_SD_per_account = [] * len(champ_df)
            contributing_per_game_K_per_account = [] * len(champ_df)
            contributing_per_game_D_per_account = [] * len(champ_df)
            contributing_per_game_A_per_account = [] * len(champ_df)
            contributing_total_KD_per_account = [] * len(champ_df)
            contributing_average_KD_per_account = [] * len(champ_df)
            contributing_average_KP_per_account = [] * len(champ_df)
            contributing_first_blood_per_account = [] * len(champ_df)
            triple_kills_per_account = [] * len(champ_df)
            quadra_kills_per_account = [] * len(champ_df)
            penta_kills_per_account = [] * len(champ_df)
            average_game_duration_per_account = [] * len(champ_df)
            role_per_account = [] * len(champ_df)

            # calculate total games for all rows
            total_games_per_champ = champ_df['total games'].sum()

            for index, row in champ_df.iterrows():

                # update account number
                account_num += 1
                account_name = player_accounts[account_num - 1]

                # contribution percentage of this account
                contribution_percentage = row['total games'] / total_games_per_champ

                # pull stats per each account per champ for the player
                total_games_per_account.append(row['total games'])
                total_wins_per_account.append(row['wins'])
                total_losses_per_account.append(row['losses'])

                # [Stat Combination] Total KDA
                contributing_total_KDA = row['total KDA'] * contribution_percentage
                contributing_total_KDA_per_account.append(contributing_total_KDA)

                # [Stat Combination] average KDA ±SD
                average_KDA_SD = row['average KDA ±SD']
                contributing_average_KDA = float(str(average_KDA_SD).split("±")[0].strip()) * contribution_percentage
                contributing_average_KDA_per_account.append(contributing_average_KDA)
                contributing_average_KDA_SD = float(str(average_KDA_SD).split("±")[1].strip()) * contribution_percentage
                contributing_average_KDA_SD_per_account.append(contributing_average_KDA_SD)

                # [Stat Combination] KDA per game
                per_game_K_D_A = row['per game K / D / A']
                contributing_per_game_K = float(str(per_game_K_D_A).split("/")[0].strip()) * contribution_percentage
                contributing_per_game_D = float(str(per_game_K_D_A).split("/")[1].strip()) * contribution_percentage
                contributing_per_game_A = float(str(per_game_K_D_A).split("/")[2].strip()) * contribution_percentage
                contributing_per_game_K_per_account.append(contributing_per_game_K)
                contributing_per_game_D_per_account.append(contributing_per_game_D)
                contributing_per_game_A_per_account.append(contributing_per_game_A)

                # [Stat Combination] Total KD
                contributing_total_KD = row['total KD'] * contribution_percentage
                contributing_total_KD_per_account.append(contributing_total_KD)

                # [Stat Combination] Average KD
                contributing_average_KD = row['average KD'] * contribution_percentage
                contributing_average_KD_per_account.append(contributing_average_KD)

                # [Stat Combination] Average KP
                average_KP = row['average KP'].replace("%", "")
                contributing_average_KP = float(average_KP) * contribution_percentage
                contributing_average_KP_per_account.append(contributing_average_KP)

                # [Stat Combination] First Blood Rate
                first_blood_rate = row['first blood rate'].replace("%", "")
                contributing_first_blood = float(first_blood_rate) * contribution_percentage
                contributing_first_blood_per_account.append(contributing_first_blood)

                # [Stat Combination] Triple Kills, Quadra Kills, Penta Kills
                triple_kills = row['triple kills']
                quadra_kills = row['quadra kills']
                penta_kills = row['penta kills']
                triple_kills_per_account.append(triple_kills)
                quadra_kills_per_account.append(quadra_kills)
                penta_kills_per_account.append(penta_kills)

                # [Stat Combination] Average Game Duration
                average_game_duration = row['average game duration']
                average_game_duration_per_account.append(average_game_duration)

                # [Stat Combination] Role
                role_per_account.append(row['role'])
                
                if in_depth_print:
                    ## PRINT OUT STATS ###
                    print(f"\n----------------")
                    print(f"(A{account_num}) {account_name} ... {champ_name}")
                    print(f"----------------")
                    print(f"{ColorPrint.CYAN}(contribution %) {round(contribution_percentage, 3)}{ColorPrint.RESET}")
                    print(f"[1] Total Games: {row['total games']}")
                    print(f"[2] Wins: {row['wins']}")
                    print(f"[3] Losses: {row['losses']}")
                    print(f"[4] Winrate: {row['winrate']}")
                    print(f"[5] Total KDA: {row['total KDA']}")
                    print(f"{ColorPrint.YELLOW}>> KDA Contribution: {contributing_total_KDA}{ColorPrint.RESET}")
                    print(f"[6] Average KDA ±SD: {row['average KDA ±SD']}")
                    print(f"{ColorPrint.YELLOW}>> KDA Contribution: {contributing_average_KDA} ± {contributing_average_KDA_SD}{ColorPrint.RESET}")
                    print(f"[7] K / D / A (per game): {row['per game K / D / A']}")
                    print(f"{ColorPrint.YELLOW}>> KDA Contribution: {contributing_per_game_K} / {contributing_per_game_D} / {contributing_per_game_A}{ColorPrint.RESET}")
                    print(f"[8] Total KD: {row['total KD']}")
                    print(f"{ColorPrint.YELLOW}>> KD Contribution: {contributing_total_KD}{ColorPrint.RESET}")
                    print(f"[9] Average KD: {row['average KD']}")
                    print(f"{ColorPrint.YELLOW}>> KD Contribution: {contributing_average_KD}{ColorPrint.RESET}")
                    print(f"[10] Average KP: {row['average KP']}")
                    print(f"{ColorPrint.YELLOW}>> KP Contribution: {contributing_average_KP}{ColorPrint.RESET}")
                    print(f"[11] First Blood Rate: {row['first blood rate']}")
                    print(f"{ColorPrint.YELLOW}>> First Blood Contribution: {contributing_first_blood}{ColorPrint.RESET}")
                    print(f"[12] Triple Kills: {row['triple kills']}")
                    print(f"[13] Quadra Kills: {row['quadra kills']}")
                    print(f"[14] Penta Kills: {row['penta kills']}")
                    print(f"[15] Average Game Duration: {row['average game duration']}")
                    print(f"[16] Role: {row['role']}")
                    print(f"----------------")
                
            ##################################################
            ### Update the new row with the combined stats ###
            ##################################################

            # create a new row as a series
            new_row = pd.Series()

            # wins, losses, total gamaes
            new_row['champion'] = champ_name
            new_row['total games'] = sum(total_games_per_account)
            new_row['wins'] = sum(total_wins_per_account)
            new_row['losses'] = sum(total_losses_per_account)

            # winrate
            winrate = sum(total_wins_per_account) / sum(total_games_per_account)
            new_row['winrate'] = str(round(winrate * 100, 2)) + "%"

            # total KDA
            player_total_KDA = sum(contributing_total_KDA_per_account)
            new_row['total KDA'] = str(round(player_total_KDA, 3))

            # average KDA ±SD
            player_average_KDA = sum(contributing_average_KDA_per_account)
            player_average_KDA_SD = sum(contributing_average_KDA_SD_per_account)
            new_row['average KDA ±SD'] = str(round(player_average_KDA, 3)) + " ± " + str(round(player_average_KDA_SD, 3))

            # per game K / D / A
            player_per_game_K = sum(contributing_per_game_K_per_account)
            player_per_game_D = sum(contributing_per_game_D_per_account)
            player_per_game_A = sum(contributing_per_game_A_per_account)
            new_row['per game K / D / A'] = str(round(player_per_game_K, 2)) + " / " + str(round(player_per_game_D, 2)) + " / " + str(round(player_per_game_A, 2))

            # total KD
            player_total_KD = sum(contributing_total_KD_per_account)
            new_row['total KD'] = str(round(player_total_KD, 2))

            # average KD
            player_average_KD = sum(contributing_average_KD_per_account)
            new_row['average KD'] = str(round(player_average_KD, 3))

            # average KP
            player_average_KP = sum(contributing_average_KP_per_account)
            new_row['average KP'] = str(round(player_average_KP, 2)) + "%"

            # first blood rate
            player_first_blood = sum(contributing_first_blood_per_account)
            new_row['first blood rate'] = str(round(player_first_blood, 2)) + "%"

            # triple kills, quadra kills, penta kills
            new_row['triple kills'] = sum(triple_kills_per_account)
            new_row['quadra kills'] = sum(quadra_kills_per_account)
            new_row['penta kills'] = sum(penta_kills_per_account)

            # average game duration
            new_row['average game duration'] = average_game_duration_per_account[0] # calculate later, for now just use the first account

            # role
            new_row['role'] = role_per_account[0] # calculate later, for now just use the first account

            # Add the new row series to the updated_player_champ_pool_df
            updated_player_champ_pool_df = pd.concat([updated_player_champ_pool_df, new_row.to_frame().T], ignore_index=True)
            
            # updated_player_champ_pool_df = updated_player_champ_pool_df.append(new_row, ignore_index=True)
            # updated_player_champ_pool_df = pd.concat([updated_player_champ_pool_df, new_row], axis=0)
            
            ###################
            ### FINAL STATS ###
            ###################
            if in_depth_print:
                print(f"\n----------------")
                print(f"[Combined Stats] {champ_name}")
                print(f"----------------")
                print(f"[1] Total Games: {new_row['total games']}")
                print(f"[2] Wins: {new_row['wins']}")
                print(f"[3] Losses: {new_row['losses']}")
                print(f"[4] Winrate: {new_row['winrate']}")
                print(f"[5] Total KDA: {new_row['total KDA']}")
                print(f"[6] Average KDA ±SD: {new_row['average KDA ±SD']}")
                print(f"[7] K / D / A (per game): {new_row['per game K / D / A']}")
                print(f"[8] Total KD: {new_row['total KD']}")
                print(f"[9] Average KD: {new_row['average KD']}")
                print(f"[10] Average KP: {new_row['average KP']}")
                print(f"[11] First Blood Rate: {new_row['first blood rate']}")
                print(f"[12] Triple Kills: {new_row['triple kills']}")
                print(f"[13] Quadra Kills: {new_row['quadra kills']}")
                print(f"[14] Penta Kills: {new_row['penta kills']}")
                print(f"[15] Average Game Duration: {new_row['average game duration']}")
                print(f"[16] Role: {new_row['role']}")
                print(f"----------------")
            
        if champ_pool_was_combined:
            # print(f"{ColorPrint.GREEN}Printing Combined Champion Stats for {player_accounts} in {pos}{ColorPrint.RESET}")
            # print(updated_player_champ_pool_df)
            # input("Press Enter to Continue...")
            pass
        else:
            print(f"{ColorPrint.RED}>> No Champion Stats Combined for {player_accounts} in {pos}{ColorPrint.RESET}!")
            input("Press Enter to Continue...")

        return updated_player_champ_pool_df


###################
### DRIVER CODE ###
###################

# MATCHA: combining multi-accounts into first Riot ID Acccount (useful fields, performing combine operations)
# ... instead of using rewind.lol ... use riot API for player champ pools
# ... do a role priority breakdown by role for everyone on a team...
# ... auto create profile on rewind.lol if not exist && auto update profile past a certain date (limit 5 for rate limiting)


