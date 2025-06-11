##########################
### Import Statements ####
##########################

# local imports
from . import update_sys_path
update_sys_path()

# data manipulation, time buffering, quick exit, csv editing
import pandas as pd
import time, sys, csv, os
import threading    # to async keep a mouse pointed at the screen while I do some processing on a dynamically generated popup

# pretty printing and color
import modules.utils.color_utils as ColorPrint

# Selenium WebDriver Options
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions    #  for FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions      # for ChromeOptions
from selenium.webdriver.firefox.service import Service                      # for FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService      # for ChromeService
from selenium.webdriver.common.by import By                                 # for locating elements BY specific types (e.g. ID, NAME, etc.)
from selenium.webdriver.common.keys import Keys                             # for clicking RETURN
from selenium.webdriver.support.ui import Select                            # for dropdown menus (element selection)
from selenium.webdriver.common.action_chains import ActionChains            # for simulation of mouse actions (like hover over element)
from selenium.webdriver.support.ui import WebDriverWait                     # for waiting for elements to load
from selenium.webdriver.support import expected_conditions as EC            # for expected conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException     # for timeout exceptions

def zephyr_print(msg):
    """
    [info] Prints formatted Zephyr system messages with colored styling
    
    [param] msg: str - Message to display
    """
    print(f"\n[[{ColorPrint.MAGENTA} Z E P H Y R {ColorPrint.RESET}]] >> {msg}...")

def warning_print(msg):
    """
    [info] Prints formatted warning messages with colored styling
    
    [param] msg: str - Warning message to display
    """
    print(f"\n[[{ColorPrint.YELLOW} WARNING {ColorPrint.RESET}]] >> {msg}...")

def error_print(msg):
    """
    [info] Prints formatted error messages with colored styling
    
    [param] msg: str - Error message to display
    """   
    print(f"\n[[{ColorPrint.RED} ERROR {ColorPrint.RESET}]] >> {msg}...")

def create_data_df(csv_file):
    """
    [info] Creates a pandas DataFrame from a CSV file
    
    [param] csv_file: str - Path to the CSV file to load
    
    [return] DataFrame: Loaded pandas DataFrame
    """
    data_df = pd.read_csv(csv_file)
    return data_df

# Profile Error: XPATH
# //*[@id="profileError"]

##################################################
### LeagueOfGraphsScraper (leagueofgraphs.com) ###
##################################################
class LeagueOfGraphsScraper:
    """
    [info] Web scraper for League of Graphs player statistics and ranking data
    
    This class provides functionality to scrape detailed player statistics, current/past rankings,
    and historical performance data from leagueofgraphs.com. Specializes in extracting peak ranks
    across multiple seasons and calculating comprehensive rank scoring.
    
    Supports multi-account analysis and season-specific rank tracking.
    """

    MAIN_WEBSITE = 'https://www.leagueofgraphs.com/'
    DRIVER = None
    BROWSER = "chrome"
    WEBSITE_TIMEOUT = 5

    ROLE_ACRYONYMS = {  
        "Top": "TOP",
        "Jungle": "JGL",
        "Mid": "MID",
        "Bot": "BOT",
        "Support": "SUP"
    }

    APEX_RANKS = ["Challenger", "Grandmaster", "Master"]

    RANK_POINTS = {
        "Iron 4": 0,       "Iron 3": 1,      "Iron 2": 2,       "Iron 1": 3,
        "Bronze 4": 4,     "Bronze 3": 5,    "Bronze 2": 6,     "Bronze 1": 7,
        "Silver 4": 8,     "Silver 3": 9,    "Silver 2": 10,    "Silver 1": 11,
        "Gold 4": 12,      "Gold 3": 13,     "Gold 2": 14,      "Gold 1": 15,
        "Platinum 4": 16,  "Platinum 3": 17, "Platinum 2": 18,  "Platinum 1": 19,
        "Emerald 4": 20,   "Emerald 3": 21,  "Emerald 2": 22,   "Emerald 1": 23,
        "Diamond 4": 24,   "Diamond 3": 25,  "Diamond 2": 26,   "Diamond 1": 27,
        "Master": 28,       "Grandmaster": 36,  "Challenger": 42,
        "Iron": 1.5, "Bronze": 5.5, "Silver": 9.5, "Gold": 13.5, "Platinum": 17.5 # metal rank averages
    }
        
    @staticmethod
    def set_up_rewind_lol():
        """
        [info] Initializes and sets up the League of Graphs website for scraping operations
        
        [return] int: 1 for success, 0 for driver already exists, -1 for error
        """
        try: 
            zephyr_print("Prepping LeagueOfGraphs")
            LeagueOfGraphsScraper.get_web_driver()
            print(f"{ColorPrint.YELLOW}LeagueOfGraphs Chrome WebDriver Loading...{ColorPrint.RESET}")
            LeagueOfGraphsScraper.DRIVER.get(LeagueOfGraphsScraper.MAIN_WEBSITE)
            print(f"{ColorPrint.GREEN}LeagueOfGraphs Chrome WebDriver Ready!{ColorPrint.RESET}")
            return 1 # success
        except Exception as e:
            print(f"Error: {e}")
            if LeagueOfGraphsScraper.DRIVER is None:
                return 0
            else:
                LeagueOfGraphsScraper.close()
            return -1 # error
        
    @staticmethod
    def load_player_profile(player_ign):
        """
        [info] Navigates to a specific player's League of Graphs profile page
        
        Handles search input, URL formatting for special characters, and error detection.
        Automatically retries with alternative URL format if initial search fails.
        
        [param] player_ign: str - Player IGN with tag (e.g., "Player#1234")
        
        [return] int or str: 1 for success, player_ign for profile not found, -1 for error
        """
        zephyr_print(f"Entering Player IGN: {player_ign}")
        try:
            # find search_box by xpath
            search_box = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='topnavbarform']/div/div[1]/input")
            search_box.send_keys(player_ign + Keys.RETURN)  # Send query and hit Enter

            # wait 5 seconds
            LeagueOfGraphsScraper.buffer()

            # check for this element, if it exists, then reload the site via another method, else continue
            error_element = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div/div[2]/div/h3")
            # print(f"{ColorPrint.YELLOW}Error Element: {error_element.text}{ColorPrint.RESET}")

            if error_element:
                # replace all spaces in player_ign with dashes
                player_ign_url_format = player_ign.replace(" ", "+").replace("#", "-")
                
                # start new window, close previous window
                url = "https://www.leagueofgraphs.com/summoner/na/" + player_ign_url_format
                LeagueOfGraphsScraper.create_new_tab_with_url(url)
                LeagueOfGraphsScraper.close_previous_tab()

                # wait 5 seconds
                LeagueOfGraphsScraper.buffer()

                # check for this element, if it exists, then reload the site via another method, else continue
                error_element = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div/div")

                if "Not Found" in error_element.text:
                    print(f"{ColorPrint.RED}[ERROR] Error accessing player profile: {player_ign}{ColorPrint.RESET}")
                    return player_ign # error
            else:
                return 1 # success
        except Exception as e:
            print(f"Error: {e}")
            return -1 # error
    
    @staticmethod
    def wait_for_element_to_load(by, value, timeout=10, custom_error_msg=None):
        """
        [info] Waits for a specific web element to load on the page
        
        [param] by: Selenium locator strategy (By.ID, By.CLASS_NAME, etc.)
        [param] value: str - The value to locate the element
        [param] timeout: int - Maximum wait time in seconds (default: 10)
        [param] custom_error_msg: str - Custom error message for timeout (optional)
        
        [return] WebElement or -1: The loaded element or -1 on timeout
        """
        try:
            element = WebDriverWait(LeagueOfGraphsScraper.DRIVER, timeout).until(
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
    def scrape_player_current_rank():
        """
        [info] Extracts player's current ranked queue statistics and ranking information
        
        Scrapes current rank, tier, LP, wins, losses, and calculates winrate.
        Handles unranked players and different rank display formats.
        
        [return] tuple: (rank_string, wins, losses, winrate) or (-1, -1, -1, -1) on error
        """
        # wait for "Personal Ratings" element to load in 
        LeagueOfGraphsScraper.wait_for_element_to_load(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/h3")

        # attempt to pull the current rank, tier, lp, wins, losses, and winrate
        try:
            tier_and_lp_together = False # flag on how tier / lp is displayed   

            # find the "Personal Rankings" element 
            personal_rankings = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]")
            # print(f"{ColorPrint.YELLOW}Personal Rankings: {personal_rankings.text}{ColorPrint.RESET}")
            
            # check if "Unranked"" is in the text
            if "Unranked" in personal_rankings.text:
                print(f"{ColorPrint.CYAN}[Current Ego Rank] Identified as {ColorPrint.GREEN}UNRANKED{ColorPrint.RESET}")
                return "UNRANKED", "0", "0", "0"
            
            # check if "Ranked Flex" is in the text via xpath
            queue_type_box = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[2]/span[1]")
            if not "Soloqueue" in queue_type_box.text:
                print(f"{ColorPrint.CYAN}[Current Ego Rank] Identified as {ColorPrint.GREEN}UNRANKED w/ some Ranked Flex{ColorPrint.RESET}")
                return "UNRANKED", "0", "0", "0"

            # find the main tier / lp element                                       
            current_ego_tier = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[1]")
            
            # if "LP" is not in the text, then find the LP element
            if "LP" not in current_ego_tier.text:
                current_ego_lp = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[4]/span")      
            else:
                tier_and_lp_together = True

            # find the wins and losses elements + calculate winrate
            current_ego_wins = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[5]/span[1]/span")
            current_ego_losses = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[5]/span[3]/span")
            calculated_current_ego_wr = round(int(current_ego_wins.text) / (int(current_ego_wins.text) + int(current_ego_losses.text)) * 100, 2)
            
            # clean up information for output
            current_ego_tier = current_ego_tier.text.replace("IV", "4").replace("III", "3").replace("II", "2").replace("I", "1").replace("1ron", "Iron")
            if tier_and_lp_together:
                current_ego_rank = current_ego_tier
            else:
                current_ego_rank = current_ego_tier + " " + current_ego_lp.text + " LP"
            
            # print ego rank, wins, losses, and winrate
            print(f"{ColorPrint.CYAN}[Current Ego Rank] {ColorPrint.GREEN}{current_ego_rank}{ColorPrint.RESET}")
            print(f"{ColorPrint.CYAN}[Current Ego Winrate] {ColorPrint.GREEN}{current_ego_wins.text}W / {current_ego_losses.text}L ... ({calculated_current_ego_wr}%){ColorPrint.RESET}")
            return current_ego_rank, current_ego_wins.text, current_ego_losses.text, calculated_current_ego_wr
        
        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error accessing player current rank: {e}{ColorPrint.RESET}")
            return -1, -1, -1, -1
        
    def keep_hovering(actions, element, duration):
        """
        [info] Maintains mouse hover over element for specified duration
        
        Used to trigger and maintain hover-based tooltips for extracting detailed rank information.
        
        [param] actions: ActionChains - Selenium action chains object
        [param] element: WebElement - Element to hover over
        [param] duration: float - Duration to maintain hover in seconds
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            actions.move_to_element(element).perform() # hover over the element
            time.sleep(0.5) # repeat hover action every 0.5 seconds (in case mouse moves or smth, also retriggers the pop up hover)

    def calculate_rank_score(rank_text):
        """
        [info] Calculates numerical score for a given rank string for comparison purposes
        
        Converts rank strings to numerical values for ranking comparison.
        Handles both standard ranks and apex ranks (Master, Grandmaster, Challenger).
        
        [param] rank_text: str - Rank string (e.g., "Gold 2 50 LP", "Master 150 LP")
        
        [return] float: Numerical rank score for comparison
        """
            rank_value = 0
            
            # print(f"{ColorPrint.CYAN}\n[Calculate - Rank Text] {ColorPrint.GREEN}{rank_text}{ColorPrint.RESET}")
            # if rank_text is pd.nan, then return 0
            if pd.isna(rank_text) or rank_text == "":
                # print(f"{ColorPrint.CYAN}[STARTING RANK VALUE] {ColorPrint.GREEN}{rank_value}{ColorPrint.RESET}")
                return rank_value 
            if "LP" not in rank_text:
                rank_text = rank_text + " 0 LP"
            
            # print(f"{ColorPrint.CYAN}[Rank Text Split] {ColorPrint.GREEN}{rank_text.split(' ')}{ColorPrint.RESET}")
            # print(f"{ColorPrint.CYAN}[Rank Text Split 0] {ColorPrint.GREEN}{rank_text.split(' ')[0]}{ColorPrint.RESET}")
            if rank_text.split(" ")[0] in LeagueOfGraphsScraper.APEX_RANKS: # if peak_ego_rank is an apex rank
                # print(f"{ColorPrint.CYAN}[rank_text.split(' ')[:1]] {ColorPrint.GREEN}{rank_text.split(' ')[:1][0]}{ColorPrint.RESET}")
                # print(f"{ColorPrint.CYAN}[rank_text.split(' ')[-2]] {ColorPrint.GREEN}{rank_text.split(' ')[-2]}{ColorPrint.RESET}")
                rank_value = LeagueOfGraphsScraper.RANK_POINTS[rank_text.split(" ")[:1][0]] + (int(rank_text.split(" ")[-2]) / 100)
                # print(f"{ColorPrint.CYAN}[Rank Score - Apex] {ColorPrint.GREEN}{rank_text} - {rank_value}{ColorPrint.RESET}")
            else:
                rank_value = LeagueOfGraphsScraper.RANK_POINTS[" ".join(rank_text.split(" ")[:2])] + (int(rank_text.split(" ")[-2]) / 100)
                # print(f"{ColorPrint.CYAN}[Rank Score] {ColorPrint.GREEN}{rank_text} - {rank_value}{ColorPrint.RESET}")
            return rank_value
    
    @staticmethod
    def scrape_player_past_peak_ranks():
        """
        [info] Extracts player's historical peak ranks across multiple seasons
        
        Scrapes season tags and uses hover interactions to extract detailed rank information.
        Processes S13/S14 season data and filters out Ranked Flex results.
        
        [return] tuple: (peak_ranks_dict, [], [], []) where peak_ranks_dict contains season->rank mapping
        """
        try:
            rank_tag_elements = []
            previous_peak_rank = {}

            # find the "Box" element containing past ranks
            tags_box = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[3]")
            
            # get all child elements of "tags_box"
            all_tags = tags_box.find_elements(By.XPATH, ".//*")

            # iterate through each tag and identify relevant ones
            for tag in all_tags:
                # if tag.text starts with "S13/S14", then keep it
                if tag.text.startswith("S13") or tag.text.startswith("S14"):
                    rank_tag_elements.append(tag)
            
            for past_rank_tag in rank_tag_elements:

                # print(f"{ColorPrint.CYAN}[Past Peak Rank] {ColorPrint.GREEN}{past_rank_tag.text}{ColorPrint.RESET}")

                # examples: "S7 Gold" ~> ["S7", "Gold"], "S12 Master" ~> ["S12", "Master"], "S13 (Split 1) Platinum" ~> ["S13 (Split 1)", "Platinum"]
                past_rank_tag_split = past_rank_tag.text.rsplit(" ", 1)

                # hover over the past_rank_tag to get the full text
                actions = ActionChains(LeagueOfGraphsScraper.DRIVER)

                # scroll to the element to prevent ad block
                y_position = past_rank_tag.location['y']
                offset = 400
                LeagueOfGraphsScraper.DRIVER.execute_script(f"window.scrollTo(0, {y_position - offset});")

                hover_thread = threading.Thread(target=LeagueOfGraphsScraper.keep_hovering, args=(actions, past_rank_tag, 1))
                hover_thread.start()

                # find the elements that contain the text "example"
                all_elements = LeagueOfGraphsScraper.DRIVER.find_elements("xpath", "//*[contains(text(), 'This player reached')]")

                for element in all_elements:
                    rank_tag_text = element.text
                    rank_tag_text = rank_tag_text.replace("\n", " ") # replace newlines with spaces
                    rank_tag_text = rank_tag_text.split("Ranked Flex")[0] # remove Ranked Flex text
                    
                    # if rank_tag_text is empty, then delete the key from the dictionary
                    if rank_tag_text == "":

                        # delete only if the key exists
                        if past_rank_tag_split[0] in previous_peak_rank:
                            del previous_peak_rank[past_rank_tag_split[0]]
    
                        # print(f"{ColorPrint.RED}[WARNING] Only Ranked Flex Found for {past_rank_tag_split[0]}{ColorPrint.RESET}")
                        break
                    else:
                        rank_tag_text = rank_tag_text.split("reached ")[1] # remove the "This player reached" text
                        rank_tag_text = rank_tag_text.split(" during")[0] # remove the " in " text
                        rank_tag_text = rank_tag_text.replace("IV", "4").replace("III", "3").replace("II", "2").replace("I", "1").replace("1ron", "Iron")
                        rank_tag_text = rank_tag_text.replace("GrandMaster", "Grandmaster") # fix Grandmaster spelling
                        rank_tag_text = rank_tag_text.replace("LP", " LP").strip() # add space before LP

                        # print(f"{ColorPrint.YELLOW}[Tag Hover Text] {ColorPrint.GREEN}{rank_tag_text}{ColorPrint.RESET}")
                        previous_peak_rank[past_rank_tag_split[0]] = rank_tag_text
                        print(f"{ColorPrint.CYAN}[Past Peak Rank] {ColorPrint.GREEN}{past_rank_tag_split[0]}{ColorPrint.RESET} ~> {ColorPrint.GREEN}{previous_peak_rank[past_rank_tag_split[0]]}{ColorPrint.RESET}")
                        

                LeagueOfGraphsScraper.buffer(time_sec=2) # wait for the hover to load

            return previous_peak_rank, [], [], []
        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error accessing player past peak ranks: {e}{ColorPrint.RESET}")
            return {}, [], [], []

    @staticmethod
    def switch_to_dark_mode():
        """
        [info] Switches the League of Graphs website interface to dark mode
        
        [return] int: 1 for success, -1 for error
        """
        zephyr_print(f"Setting Dark Mode")
        try:
            # find the slider by xpath
            dark_mode_slider = LeagueOfGraphsScraper.DRIVER.find_element(By.XPATH, "//*[@id='topnavbar']/nav/section/ul[1]/li[1]/div/label/span")
            
            # click the slider
            dark_mode_slider.click()
            
            return 1 # success
        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error Switching to Dark Mode: {e}{ColorPrint.RESET}")
            return -1 # error

    @staticmethod
    def get_web_driver():
        """
        [info] Sets up and configures the WebDriver for automated browser access
        
        Supports both Firefox and Chrome browsers with headless operation.
        Configures browser options for optimal scraping performance.
        
        [return] int: 1 if driver created, 0 if driver already exists
        """
        if LeagueOfGraphsScraper.DRIVER is None:
            zephyr_print("Setting up Chrome WebDriver")
            if LeagueOfGraphsScraper.BROWSER.lower() == "firefox":
                options = FirefoxOptions()
                options.headless = True  # Runs in headless mode, no UI.
                service = Service('/path/to/geckodriver')  # Path to geckodriver
                LeagueOfGraphsScraper.DRIVER = webdriver.Firefox(service=service, options=options)
            elif LeagueOfGraphsScraper.BROWSER.lower() == "chrome":
                options = ChromeOptions()
                options.headless = True  # Runs in headless mode, no UI.
                options.add_argument("--start-maximized")
                options.page_load_strategy = 'eager'  # Eager page loading will load the page as soon as possible
                service = ChromeService('/opt/homebrew/bin/chromedriver')  # Path to chromedriver
                LeagueOfGraphsScraper.DRIVER = webdriver.Chrome(service=service, options=options)
            else:
                raise ValueError("Only 'firefox' and 'chrome' browsers are supported.")
            return 1 # driver created
        else:
            return 0 # driver already exists

    def buffer(time_sec = WEBSITE_TIMEOUT):
        """
        [info] Adds a time buffer/delay for website loading and rate limiting
        
        [param] time_sec: int - Duration to wait in seconds (default: WEBSITE_TIMEOUT)
        """
        time.sleep(time_sec)

    @staticmethod
    def close():
        """
        [info] Closes the WebDriver and cleans up browser resources
        """
        LeagueOfGraphsScraper.DRIVER.quit()

    @staticmethod
    def close_previous_tab():
        """
        [info] Closes the previous browser tab and switches to the latest tab
        """
        # Get a list of all open tabs
        tabs = LeagueOfGraphsScraper.DRIVER.window_handles

        # Switch to the previous tab
        LeagueOfGraphsScraper.DRIVER.switch_to.window(tabs[0])

        # Close the Current Tab
        LeagueOfGraphsScraper.DRIVER.close()

        # Switch to the previous tab open
        LeagueOfGraphsScraper.DRIVER.switch_to.window(tabs[-1]) # tabs[-1] is the last tab opened 

    @staticmethod
    def create_new_tab():
        """
        [info] Opens a new browser tab with League of Graphs homepage
        """
        # Load a new instance of LeagueOfGraphs in new tab
        LeagueOfGraphsScraper.DRIVER.execute_script("window.open('https://www.leagueofgraphs.com', '_blank');")

    @staticmethod
    def create_new_tab_with_url(url):
        """
        [info] Opens a new browser tab with the specified URL
        
        [param] url: str - URL to open in the new tab
        """
        # Load a new instance of LeagueOfGraphs in new tab
        LeagueOfGraphsScraper.DRIVER.execute_script(f"window.open('{url}', '_blank');")

    @staticmethod
    def exportable_update_player_rank(profile_ign_list):
        """
        [info] Batch processes multiple player profiles for rank updates
        
        Sets up scraping environment and processes a list of player IGNs for rank extraction.
        
        [param] profile_ign_list: list[str] - List of player IGNs to process
        """
        # expects a list of profile_igns in list form 
        setup = False
        profile_ign_list = [ign.strip() for ign in profile_ign_list]

        if not setup:
            LeagueOfGraphsScraper.set_up_rewind_lol()
            status = LeagueOfGraphsScraper.switch_to_dark_mode()
            setup = True




# ###################
# ### DRIVER CODE ###
# ###################

# input_data_file = 'data/raw/gcs_roster_info.csv'
# output_data_file = 'data/synthesized/gcs_roster_info_additive.csv'
# gcs_roster = create_data_df(input_data_file)

# # create copy of gcs_roster
# gcs_roster_additive = gcs_roster.copy()

# # iterate through each row in the gcs_roster
# setup = False
# counter = 1
# execute = False

# for index, row in gcs_roster.iterrows():

#     team_name = row['Team Name']

#     # # if player is not on a team, don't scrape info on them
#     if team_name == "" or pd.isna(team_name):
#         continue

#     # if not team_name == "MDFC":
#     #     continue

#     # obtain clean profile_igns
#     profile_ign = row['Summoner IGN']
    
#     if profile_ign == "" or pd.isna(profile_ign):
#         continue # skip if profile_ign is empty

#     print(f"{ColorPrint.YELLOW}\n[{profile_ign}]\nRow:\n{row}{ColorPrint.RESET}")
#     print(f"{ColorPrint.YELLOW}[Counter] {counter}{ColorPrint.RESET}")

#     # if "Brandis#0704" in profile_ign:
#     #     execute = True

#     # if not execute:
#     #     continue 

#     # if not profile_ign == "hackzorzzzz#NA1|Bengar#6969|UNC is Gapped#LUL|WATCH ME PLAYING#NA2" and not profile_ign == "PeepaTheHound#Molly|Doublethink#Orew|GeppettosPuppet#3671|PositiveEV#1111|Winston The Pooh#Win|ZUPER ZA1YAN#NA1":
#     #     continue
    
#     # make a copy of the 'row'
#     profile_max_output = row.copy()
#     profile_max_output['Current Ego Rank'] = ""
#     profile_max_output['Peak Ego Rank'] = ""
#     profile_max_output['True Peak Rank'] = ""
#     profile_max_output['Peak Ego Rank'] = ""
#     profile_max_output['S2024 S3 Peak'] = ""
#     profile_max_output['S2024 S2 Peak'] = ""
#     profile_max_output['S2024 S1 Peak'] = ""
#     profile_max_output['S2023 S2 Peak'] = ""
#     profile_max_output['S2023 S1 Peak'] = ""

#     print(f"{ColorPrint.YELLOW}\n[{profile_max_output['Summoner IGN']}]\nMax Output:\n{profile_max_output}{ColorPrint.RESET}")

#     # if multiple profiles, splice into a profile list
#     profile_ign_list = []
#     problem_profiles = []
#     if "|" in profile_ign:
#         profile_ign_list = profile_ign.split("|")
#     else:
#         profile_ign_list.append(profile_ign)
#     profile_ign_list = [ign.strip() for ign in profile_ign_list]

#     # setup the LeagueOfGraphs website for scraping as needed
#     if not setup:
#         LeagueOfGraphsScraper.set_up_rewind_lol()
#         status = LeagueOfGraphsScraper.switch_to_dark_mode()
#         setup = True

#     # iterate through each profile_ign in the list
#     # profile_ign_list = ["Haumea#GCS, BioMatrix#Dead"]
#     for profile_ign in profile_ign_list:
#         status = LeagueOfGraphsScraper.load_player_profile(profile_ign)
#         if status == profile_ign:
#             problem_profiles.append(profile_ign)
#             # store a copy of problem profiles into the output txt file at data/synthesized/problem_profiles.txt
#             with open('data/synthesized/problem_profiles.txt', 'a') as f:
#                 f.write(f"{profile_ign}\n")            
#             continue
#         zephyr_print(f"Scraping {profile_ign} Current Ego Rank, Wins, Losses, and Winrate")
#         current_ego_rank, current_ego_rank_wins, current_ego_rank_losses, current_ego_rank_wr = LeagueOfGraphsScraper.scrape_player_current_rank()

#         # if there is no current ego rank, wait for user input then move on
#         if current_ego_rank == -1:
#             print(f"{ColorPrint.RED}[ERROR] Error accessing player current rank: {profile_ign}{ColorPrint.RESET}")
#             input("Press Enter to Quit...")
#             sys.exit()

#         # save a copy of the last profile "Current Ego Rank" if needed
#         old_current_ego_rank = profile_max_output['Current Ego Rank']

#         # if peak ego rank is not initialized, initialize to current_ego_rank
#         if profile_max_output['Peak Ego Rank'] == "":
#             profile_max_output['Peak Ego Rank'] = old_current_ego_rank
#             print(f"{ColorPrint.CYAN}Created Peak Ego Rank for {ColorPrint.GREEN}{profile_ign}{ColorPrint.CYAN} to {ColorPrint.GREEN}{old_current_ego_rank}{ColorPrint.RESET}")

#         # if the current_ego_rank is empty, update the current_ego_rank
#         if old_current_ego_rank == "":
#             if current_ego_rank == "UNRANKED":
#                 profile_max_output['Current Ego Rank'] = ""
#                 profile_max_output['Peak Ego Rank'] = ""
#                 print(f"{ColorPrint.CYAN}Created Current Ego Rank for {ColorPrint.GREEN}{profile_ign}{ColorPrint.CYAN} to {ColorPrint.RED}UNRANKED{ColorPrint.RESET}")
#             else:
#                 profile_max_output['Current Ego Rank'] = current_ego_rank
#                 profile_max_output['Peak Ego Rank'] = current_ego_rank
#                 print(f"{ColorPrint.CYAN}\nCreated Current & Peak Ego Rank for {ColorPrint.GREEN}{profile_ign}{ColorPrint.CYAN} to {ColorPrint.GREEN}{current_ego_rank}{ColorPrint.RESET}")
#         # if another profile has a current ego rank that is lower, update the current_ego_rank
#         elif profile_max_output['Current Ego Rank'] != current_ego_rank:
            
#             if current_ego_rank == "UNRANKED":
#                 print(f"{ColorPrint.CYAN}\nKept (EXISTING) Ego Rank ({profile_max_output['Current Ego Rank']}) of {ColorPrint.GREEN}{profile_ign}{ColorPrint.CYAN} instead of shifting to {ColorPrint.RED}UNRANKED{ColorPrint.RESET}")
#             else:
#                 old_current_ego_rank_value = LeagueOfGraphsScraper.calculate_rank_score(old_current_ego_rank)
#                 new_current_ego_rank_value = LeagueOfGraphsScraper.calculate_rank_score(current_ego_rank)
#                 peak_ego_rank_value = LeagueOfGraphsScraper.calculate_rank_score(profile_max_output['Peak Ego Rank'])

#                 # update the current_ego_rank if the current_ego_rank_value is higher than the old_current_ego_rank_value
#                 if new_current_ego_rank_value > old_current_ego_rank_value:
#                     profile_max_output['Current Ego Rank'] = current_ego_rank
#                     print(f"{ColorPrint.GREEN}\nUpdated Current Ego Rank for {ColorPrint.CYAN}{profile_ign}{ColorPrint.GREEN} to {ColorPrint.CYAN}{current_ego_rank}{ColorPrint.RESET}")
#                 else:
#                     print(f"{ColorPrint.RED}\nCurrent Ego Rank {ColorPrint.GREEN}{old_current_ego_rank}{ColorPrint.RED} for {ColorPrint.GREEN}{profile_ign}{ColorPrint.RED} is already higher than {ColorPrint.YELLOW}{current_ego_rank}{ColorPrint.RESET}")

#                 # update the peak_ego_rank if the current_ego_rank_value is higher than the peak_ego_rank_value
#                 if new_current_ego_rank_value > peak_ego_rank_value:
#                     profile_max_output['Peak Ego Rank'] = current_ego_rank
#                     print(f"{ColorPrint.GREEN}Updated Peak Ego Rank for {ColorPrint.CYAN}{profile_ign}{ColorPrint.GREEN} to {ColorPrint.CYAN}{current_ego_rank}{ColorPrint.RESET}")

#         zephyr_print(f"Scraping {profile_ign} Previous Peak Rank, Wins, Losses, and Winrate")
#         previous_peak_rank, previous_rank_wins, previous_rank_losses, previous_rank_wr = LeagueOfGraphsScraper.scrape_player_past_peak_ranks()
        
#         # if previous_peak_rank is and empty dict 
#         if previous_peak_rank == -1: # this signifies that the dict is empty
#             print(f"{ColorPrint.RED}[ERROR] Error accessing player past peak ranks: {profile_ign}{ColorPrint.RESET}")
#             input("Press Enter to Quit...")
#             sys.exit()

#         # update split ranks & true peak ranks as needed 
#         for key, item in previous_peak_rank.items():
#             # print(f"\n{ColorPrint.CYAN}[SPLIT] {ColorPrint.GREEN}{key}{ColorPrint.RESET}")
#             # print(f"\t{ColorPrint.YELLOW}[PEAK RANK] {item}{ColorPrint.RESET}")
#             item_rank_score = LeagueOfGraphsScraper.calculate_rank_score(item)
#             prior_true_peak_rank_value = LeagueOfGraphsScraper.calculate_rank_score(profile_max_output['True Peak Rank'])
#             if item_rank_score > prior_true_peak_rank_value:
#                 profile_max_output['True Peak Rank'] = item
#                 print(f"\n{ColorPrint.CYAN}>>> Updated True Peak Rank to {ColorPrint.GREEN}{item}{ColorPrint.RESET}")
#             match (key):
#                 case ("S13 (Split 1)"):
#                     s13_split1_rank_score = LeagueOfGraphsScraper.calculate_rank_score(profile_max_output['S2023 S1 Peak'])
#                     if item_rank_score > s13_split1_rank_score:
#                         profile_max_output['S2023 S1 Peak'] = item
#                         print(f"\n{ColorPrint.CYAN}>>> Updated S2023 S1 Peak to {ColorPrint.GREEN}{item}{ColorPrint.RESET}")
#                     else:
#                         print(f"\n{ColorPrint.RED}S2023 S1 Peak {ColorPrint.GREEN}{profile_max_output['S2023 S1 Peak']}{ColorPrint.RED} is already higher than {ColorPrint.YELLOW}{item}{ColorPrint.RESET}")
#                 case ("S13 (Split 2)"):
#                     s13_split2_rank_score = LeagueOfGraphsScraper.calculate_rank_score(profile_max_output['S2023 S2 Peak'])
#                     if item_rank_score > s13_split2_rank_score:
#                         profile_max_output['S2023 S2 Peak'] = item
#                         print(f"\n{ColorPrint.CYAN}>>> Updated S2023 S2 Peak to {ColorPrint.GREEN}{item}{ColorPrint.RESET}")
#                     else:
#                         print(f"\n{ColorPrint.RED}S2023 S2 Peak {ColorPrint.GREEN}{profile_max_output['S2023 S2 Peak']}{ColorPrint.RED} is already higher than {ColorPrint.YELLOW}{item}{ColorPrint.RESET}")
#                 case ("S14 (Split 1)"):
#                     s14_split1_rank_score = LeagueOfGraphsScraper.calculate_rank_score(profile_max_output['S2024 S1 Peak'])
#                     if item_rank_score > s14_split1_rank_score:
#                         profile_max_output['S2024 S1 Peak'] = item
#                         print(f"\n{ColorPrint.CYAN}>>> Updated S2024 S1 Peak to {ColorPrint.GREEN}{item}{ColorPrint.RESET}")
#                     else:
#                         print(f"\n{ColorPrint.RED}S2024 S1 Peak {ColorPrint.GREEN}{profile_max_output['S2024 S1 Peak']}{ColorPrint.RED} is already higher than {ColorPrint.YELLOW}{item}{ColorPrint.RESET}")
#                 case ("S14 (Split 2)"):
#                     s14_split2_rank_score = LeagueOfGraphsScraper.calculate_rank_score(profile_max_output['S2024 S2 Peak'])
#                     if item_rank_score > s14_split2_rank_score:
#                         profile_max_output['S2024 S2 Peak'] = item
#                         print(f"\n{ColorPrint.CYAN}>>> Updated S2024 S2 Peak to {ColorPrint.GREEN}{item}{ColorPrint.RESET}")
#                     else:
#                         print(f"\n{ColorPrint.RED}S2024 S2 Peak {ColorPrint.GREEN}{profile_max_output['S2024 S2 Peak']}{ColorPrint.RED} is already higher than {ColorPrint.YELLOW}{item}{ColorPrint.RESET}")
#                 case ("S14 (Split 3)"):
#                     s14_split3_rank_score = LeagueOfGraphsScraper.calculate_rank_score(profile_max_output['S2024 S3 Peak'])
#                     if item_rank_score > s14_split3_rank_score:
#                         profile_max_output['S2024 S3 Peak'] = item
#                         print(f"\n{ColorPrint.CYAN}>>> Updated S2024 S3 Peak to {ColorPrint.GREEN}{item}{ColorPrint.RESET}")
#                     else:
#                         print(f"\n{ColorPrint.RED}S2024 S3 Peak {ColorPrint.GREEN}{profile_max_output['S2024 S3 Peak']}{ColorPrint.RED} is already higher than {ColorPrint.YELLOW}{item}{ColorPrint.RESET}")

#         print(f"{ColorPrint.CYAN}\n[{profile_ign}]\nMax Output:\n{profile_max_output}{ColorPrint.RESET}")
#         LeagueOfGraphsScraper.buffer()
#         LeagueOfGraphsScraper.create_new_tab()
#         LeagueOfGraphsScraper.close_previous_tab()
    
#     # print profile_max_output
#     print(f"{ColorPrint.CYAN}\n[{profile_max_output['Summoner IGN']}]\nMax Output:\n{profile_max_output}{ColorPrint.RESET}")

#     # apply the changes in data we made to profile_max_output to the gcs_roster and gcs_roster_additive
#     gcs_roster.loc[index] = profile_max_output
#     gcs_roster_additive.loc[index] = profile_max_output

#     # store temp copy of gcs roster and gcs_roster_additive into the csv file
#     # gcs_roster.to_csv(input_data_file, index=False)
#     # gcs_roster_additive.to_csv(output_data_file, index=False)

#     # # wait for user input
#     input("Press Enter to continue...")
#     counter += 1

# LeagueOfGraphsScraper.close()

# # TODO
# # take previous_peak_ranks ~> add to the the df
# # add wr or # of total games / champs played per season in parentheses

