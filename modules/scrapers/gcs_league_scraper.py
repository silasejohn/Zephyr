##########################
### Import Statements ####
##########################

# local imports
from __init__ import update_sys_path
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
    print(f"\n[[{ColorPrint.MAGENTA} Z E P H Y R {ColorPrint.RESET}]] >> {msg}...")

def warning_print(msg):
    print(f"\n[[{ColorPrint.YELLOW} WARNING {ColorPrint.RESET}]] >> {msg}...")

def error_print(msg):   
    print(f"\n[[{ColorPrint.RED} ERROR {ColorPrint.RESET}]] >> {msg}...")

def create_data_df(csv_file):
    data_df = pd.read_csv(csv_file)
    return data_df

# Profile Error: XPATH
# //*[@id="profileError"]

##################################################
### GCS_LEAGUE (gcsleague.com) ###
##################################################
class GCSLeagueScraper:

    MAIN_WEBSITE = 'https://www.gcsleague.com/seasons/2'
    # MAIN_WEBSITE = 'https://www.gcsleague.com/teams/'
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
    # sets up the GCSLEAGUE website
    def set_up_gcs_league():
        try: 
            zephyr_print("Prepping GCSLeague")
            GCSLeagueScraper.get_web_driver()
            print(f"{ColorPrint.YELLOW}GCSLeague Chrome WebDriver Loading...{ColorPrint.RESET}")
            GCSLeagueScraper.DRIVER.get(GCSLeagueScraper.MAIN_WEBSITE)
            print(f"{ColorPrint.GREEN}GCSLeague Chrome WebDriver Ready!{ColorPrint.RESET}")
            return 1 # success
        except Exception as e:
            print(f"Error: {e}")
            if GCSLeagueScraper.DRIVER is None:
                return 0
            else:
                GCSLeagueScraper.close()
            return -1 # error
        
    @staticmethod
    # enter in player IGN and arrive at their GCSLeague profile page
    def load_player_profile(player_ign):
        zephyr_print(f"Entering Player IGN: {player_ign}")
        try:
            # find search_box by xpath
            search_box = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='topnavbarform']/div/div[1]/input")
            search_box.send_keys(player_ign + Keys.RETURN)  # Send query and hit Enter

            # wait 5 seconds
            GCSLeagueScraper.buffer()

            # check for this element, if it exists, then reload the site via another method, else continue
            error_element = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div/div[2]/div/h3")
            # print(f"{ColorPrint.YELLOW}Error Element: {error_element.text}{ColorPrint.RESET}")

            if error_element:
                # replace all spaces in player_ign with dashes
                player_ign_url_format = player_ign.replace(" ", "+").replace("#", "-")
                
                # start new window, close previous window
                url = "https://www.leagueofgraphs.com/summoner/na/" + player_ign_url_format
                GCSLeagueScraper.create_new_tab_with_url(url)
                GCSLeagueScraper.close_previous_tab()

                # wait 5 seconds
                GCSLeagueScraper.buffer()

                # check for this element, if it exists, then reload the site via another method, else continue
                error_element = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div/div")

                if "Not Found" in error_element.text:
                    print(f"{ColorPrint.RED}[ERROR] Error accessing player profile: {player_ign}{ColorPrint.RESET}")
                    return player_ign # error
            else:
                return 1 # success
        except Exception as e:
            print(f"Error: {e}")
            return -1 # error
    
    @staticmethod
    # waits for an "element" to show up on page
    # used to wait for page (and specific element) to load
    def wait_for_element_to_load(by, value, timeout=10, custom_error_msg=None):
        try:
            element = WebDriverWait(GCSLeagueScraper.DRIVER, timeout).until(
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
    def scrape_player_current_rank():
        # wait for "Personal Ratings" element to load in 
        GCSLeagueScraper.wait_for_element_to_load(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/h3")

        # attempt to pull the current rank, tier, lp, wins, losses, and winrate
        try:
            tier_and_lp_together = False # flag on how tier / lp is displayed   

            # find the "Personal Rankings" element 
            personal_rankings = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]")
            # print(f"{ColorPrint.YELLOW}Personal Rankings: {personal_rankings.text}{ColorPrint.RESET}")
            
            # check if "Unranked"" is in the text
            if "Unranked" in personal_rankings.text:
                print(f"{ColorPrint.CYAN}[Current Ego Rank] Identified as {ColorPrint.GREEN}UNRANKED{ColorPrint.RESET}")
                return "UNRANKED", "0", "0", "0"
            
            # check if "Ranked Flex" is in the text via xpath
            queue_type_box = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[2]/span[1]")
            if not "Soloqueue" in queue_type_box.text:
                print(f"{ColorPrint.CYAN}[Current Ego Rank] Identified as {ColorPrint.GREEN}UNRANKED w/ some Ranked Flex{ColorPrint.RESET}")
                return "UNRANKED", "0", "0", "0"

            # find the main tier / lp element                                       
            current_ego_tier = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[1]")
            
            # if "LP" is not in the text, then find the LP element
            if "LP" not in current_ego_tier.text:
                current_ego_lp = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[4]/span")      
            else:
                tier_and_lp_together = True

            # find the wins and losses elements + calculate winrate
            current_ego_wins = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[5]/span[1]/span")
            current_ego_losses = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[5]/span[3]/span")
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
        end_time = time.time() + duration
        while time.time() < end_time:
            actions.move_to_element(element).perform() # hover over the element
            time.sleep(0.5) # repeat hover action every 0.5 seconds (in case mouse moves or smth, also retriggers the pop up hover)

    def calculate_rank_score(rank_text):
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
            if rank_text.split(" ")[0] in GCSLeagueScraper.APEX_RANKS: # if peak_ego_rank is an apex rank
                # print(f"{ColorPrint.CYAN}[rank_text.split(' ')[:1]] {ColorPrint.GREEN}{rank_text.split(' ')[:1][0]}{ColorPrint.RESET}")
                # print(f"{ColorPrint.CYAN}[rank_text.split(' ')[-2]] {ColorPrint.GREEN}{rank_text.split(' ')[-2]}{ColorPrint.RESET}")
                rank_value = GCSLeagueScraper.RANK_POINTS[rank_text.split(" ")[:1][0]] + (int(rank_text.split(" ")[-2]) / 100)
                # print(f"{ColorPrint.CYAN}[Rank Score - Apex] {ColorPrint.GREEN}{rank_text} - {rank_value}{ColorPrint.RESET}")
            else:
                rank_value = GCSLeagueScraper.RANK_POINTS[" ".join(rank_text.split(" ")[:2])] + (int(rank_text.split(" ")[-2]) / 100)
                # print(f"{ColorPrint.CYAN}[Rank Score] {ColorPrint.GREEN}{rank_text} - {rank_value}{ColorPrint.RESET}")
            return rank_value
    
    @staticmethod
    # scrapes players past peak ranks
    # previous_peak_rank, previous_rank_wins, previous_rank_losses, previous_rank_wr
    def scrape_player_past_peak_ranks():
        try:
            rank_tag_elements = []
            previous_peak_rank = {}

            # find the "Box" element containing past ranks
            tags_box = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='mainContent']/div[1]/div[1]/div[3]")
            
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
                actions = ActionChains(GCSLeagueScraper.DRIVER)

                # scroll to the element to prevent ad block
                y_position = past_rank_tag.location['y']
                offset = 400
                GCSLeagueScraper.DRIVER.execute_script(f"window.scrollTo(0, {y_position - offset});")

                hover_thread = threading.Thread(target=GCSLeagueScraper.keep_hovering, args=(actions, past_rank_tag, 1))
                hover_thread.start()

                # find the elements that contain the text "example"
                all_elements = GCSLeagueScraper.DRIVER.find_elements("xpath", "//*[contains(text(), 'This player reached')]")

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
                        

                GCSLeagueScraper.buffer(time_sec=2) # wait for the hover to load

            return previous_peak_rank, [], [], []
        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error accessing player past peak ranks: {e}{ColorPrint.RESET}")
            return {}, [], [], []

    @staticmethod
    # switch to dark mode
    def switch_to_dark_mode():
        zephyr_print(f"Setting Dark Mode")
        try:
            # find the slider by xpath
            dark_mode_slider = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "//*[@id='topnavbar']/nav/section/ul[1]/li[1]/div/label/span")
            
            # click the slider
            dark_mode_slider.click()
            
            return 1 # success
        except Exception as e:
            print(f"{ColorPrint.RED}[ERROR] Error Switching to Dark Mode: {e}{ColorPrint.RESET}")
            return -1 # error

    @staticmethod
    # sets up the webdriver (automated chrome access)
    # [returns] 1 if driver created, 0 if driver already exists
    def get_web_driver():
        if GCSLeagueScraper.DRIVER is None:
            zephyr_print("Setting up Chrome WebDriver")
            if GCSLeagueScraper.BROWSER.lower() == "firefox":
                options = FirefoxOptions()
                options.headless = True  # Runs in headless mode, no UI.
                service = Service('/path/to/geckodriver')  # Path to geckodriver
                GCSLeagueScraper.DRIVER = webdriver.Firefox(service=service, options=options)
            elif GCSLeagueScraper.BROWSER.lower() == "chrome":
                options = ChromeOptions()
                options.headless = True  # Runs in headless mode, no UI.
                options.add_argument("--start-maximized")
                options.page_load_strategy = 'eager'  # Eager page loading will load the page as soon as possible
                service = ChromeService('/opt/homebrew/bin/chromedriver')  # Path to chromedriver
                GCSLeagueScraper.DRIVER = webdriver.Chrome(service=service, options=options)
            else:
                raise ValueError("Only 'firefox' and 'chrome' browsers are supported.")
            return 1 # driver created
        else:
            return 0 # driver already exists

    def buffer(time_sec = WEBSITE_TIMEOUT):
        time.sleep(time_sec)

    @staticmethod
    def close():
        GCSLeagueScraper.DRIVER.quit()

    @staticmethod   
    def close_previous_tab():
        # Get a list of all open tabs
        tabs = GCSLeagueScraper.DRIVER.window_handles

        # Switch to the previous tab
        GCSLeagueScraper.DRIVER.switch_to.window(tabs[0])

        # Close the Current Tab
        GCSLeagueScraper.DRIVER.close()

        # Switch to the previous tab open
        GCSLeagueScraper.DRIVER.switch_to.window(tabs[-1]) # tabs[-1] is the last tab opened 

    @staticmethod
    def create_new_tab():
        # Load a new instance of GCSLeague in new tab
        GCSLeagueScraper.DRIVER.execute_script("window.open('https://www.leagueofgraphs.com', '_blank');")

    @staticmethod
    def create_new_tab_with_url(url):
        # Load a new instance of GCSLeague in new tab
        GCSLeagueScraper.DRIVER.execute_script(f"window.open('{url}', '_blank');")

    @staticmethod
    def exportable_update_player_rank(profile_ign_list):
        # expects a list of profile_igns in list form 
        setup = False
        profile_ign_list = [ign.strip() for ign in profile_ign_list]

        if not setup:
            GCSLeagueScraper.set_up_gcs_league()
            status = GCSLeagueScraper.switch_to_dark_mode()
            setup = True