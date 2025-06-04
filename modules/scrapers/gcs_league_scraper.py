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
    def standardize_position(non_standard_position_name):
        position_map = {
            "TOP": "TOP",
            "JUNGLE": "JGL",
            "MIDDLE": "MID",
            "BOTTOM": "BOT",
            "UTILITY": "SUP"
        }
        output = position_map.get(non_standard_position_name.upper(), -1)  # convert to uppercase for matching
        if output == -1:
            warning_print(f"Non-standard position name '{non_standard_position_name}' encountered. Returning -1.")
        return output