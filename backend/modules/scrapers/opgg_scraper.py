##########################
### Import Statements ####
##########################

# local imports
from . import update_sys_path
update_sys_path()

# data manipulation, time buffering, quick exit, csv editing, random number generation, json
import os, sys
import time
import csv
from random import randint
import json

# web scraping imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

# color utils
from modules.utils.color_utils import warning_print, error_print, info_print, success_print

###########################
### OPGGScraper (op.gg) ###
###########################
class OPGGScraper:
    """
    [info] Web scraper for OP.GG League of Legends player statistics and ranking data
    
    This class provides functionality to scrape player statistics, rank information,
    and match history data from op.gg, a popular League of Legends statistics website.
    
    Supports both single player lookups and multi-search queries for batch processing.
    Includes automatic rank scoring system and profile type detection.
    """

    # Main Website for League of Legends OP.GG
    MAIN_WEBSITE = "https://www.op.gg/"
    DRIVER = None
    BROWSER = "chrome"
    WEBSITE_TIMEOUT = 8

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

    # class variables for profile type
    isProfileSummonerIGN = False # could be list of multiple IGNs as well
    isProfileSingleSearch = False
    isProfileMultiSearch = False
    isProfileNonStandard = False # u.gg, leagueofgraphs, etc. 

    @staticmethod
    def reset_bool_flags_to_false():
        """
        [info] Resets all profile type flags to False for clean query processing
        
        Used to ensure clean state before processing new queries.
        """
        OPGGScraper.isProfileSummonerIGN = False
        OPGGScraper.isProfileSingleSearch = False
        OPGGScraper.isProfileMultiSearch = False
        OPGGScraper.isProfileNonStandard = False

    @staticmethod
    def set_up_opgg():
        """
        [info] Initializes and sets up the OP.GG website for scraping operations
        
        [return] int: 1 for success, 0 for driver already exists, -1 for error
        """
        try: 
            info_print("Prepping OPGG")
            OPGGScraper.get_web_driver()
            warning_print("OPGG Chrome WebDriver Loading...")
            OPGGScraper.DRIVER.get(OPGGScraper.MAIN_WEBSITE)
            success_print("OPGG Chrome WebDriver Ready!")
            return 1 # success
        except Exception as e:
            print(f"Error: {e}")
            if OPGGScraper.DRIVER is None:
                return 0
            else:
                OPGGScraper.close()
            return -1 # error
        
    @staticmethod
    def get_web_driver():
        """
        [info] Sets up and returns the WebDriver for automated browser access
        
        Supports both Firefox and Chrome browsers with headless operation.
        Configures browser service and options for web scraping.
        
        [return] WebDriver: Configured browser driver instance
        """
        """Sets up and returns the WebDriver (Firefox or Chrome)."""
        info_print("Setting up Chrome WebDriver")
        
        if OPGGScraper.BROWSER.lower() == "firefox":
            options = FirefoxOptions()
            options.headless = True  # Runs in headless mode, no UI.
            service = Service('/path/to/geckodriver')  # Path to geckodriver
            OPGGScraper.DRIVER = webdriver.Firefox(service=service, options=options)
        elif OPGGScraper.BROWSER.lower() == "chrome":
            options = ChromeOptions()
            options.headless = True  # Runs in headless mode, no UI.
            service = ChromeService('/opt/homebrew/bin/chromedriver')  # Path to chromedriver
            OPGGScraper.DRIVER = webdriver.Chrome(service=service, options=options)
        else:
            raise ValueError("Only 'firefox' and 'chrome' browsers are supported.")

        return OPGGScraper.DRIVER
    
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
            element = WebDriverWait(OPGGScraper.DRIVER, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            if custom_error_msg:
                error_print(f"{custom_error_msg}")
            else:
                error_print(f"Element not Found! {by} {value}")
            return -1
    
    @staticmethod
    def query_summoner_stats(original_query, sleep=True):
        """
        [info] Main function to fetch and retrieve comprehensive summoner statistics
        
        Processes query input, handles multiple profile types, and extracts summoner data.
        Supports single searches, multi-searches, and IGN-based queries.
        
        [param] original_query: str - The query string (URL or IGN)
        [param] sleep: bool - Whether to add random delays (default: True)
        
        [return] str or list: Summoner IGN(s) or profile list, -1 on error
        """

        info_print("Querying Summoner Stats")
        # reset all flags for a new query
        OPGGScraper.reset_bool_flags_to_false()

        if sleep:
            time.sleep(randint(3, 7))  # Random sleep

        info_print(original_query, header="INCOMING QUERY")

        # Identify the query input
        query_list, summoner_profiles = OPGGScraper.identify_query_input(original_query)
        if query_list[0] == -1:
            error_print("Invalid OP.GG LINK!")
            # wait for user input 
            warning_print("Press <ENTER> to continue...")
            input()
            return -1, -1
        time.sleep(0.5)  # Random sleep

        # reset rank_info
        OPGGScraper.rank_info = {}

        query_counter = 1
        summoner_ign = "nondescript_profile_name"

        if OPGGScraper.DRIVER is None:
            OPGGScraper.DRIVER = OPGGScraper.get_web_driver()  # Initialize WebDriver

        print(f"Query List: {query_list} && Summoner Profiles: {summoner_profiles}")

        for query in query_list:
            # if size of summoner profiles is bigger than 1, print the current profile
            if len(summoner_profiles) > 1:
                warning_print(f"\nExtracting Profile {query_counter}: {summoner_profiles[query_counter - 1]}")
            else: 
                warning_print(f"\nExtracting Profile {query_counter}: {query}")
            query_counter += 1

            # Handle the query input
            query_list = OPGGScraper.handle_query_input(query)
            time.sleep(0.5)  # Random sleep

            # MATCHA: Update the summoner profile
            # status = OPGGScraper.update_opgg_summoner_profile()
            # time.sleep(0.5)  # Random sleep

            # MATCHA: update the summoner profile
            # if status == -1:
            #     error_print("Failed to Access Player Profile!")
            #     # wait for user input 
            #     warning_print("Press <ENTER> to continue...")
            #     input()
            #     continue

            # MATCHA: Expand the match history
            # OPGGScraper.expand_match_history()
            # time.sleep(0.5)  # Random sleep

            # Identify the summoner IGN
            summoner_ign = OPGGScraper.scrape_summoner_ign()
            time.sleep(0.5)  # Random sleep

            # MATCHA: Identify current season peak rank
            # OPGGScraper.scrape_rank_info(summoner_ign)
            # time.sleep(0.5)  # Random sleep

        # # Calculate the peak rank across multiple accounts and seasons
        # output = OPGGScraper.calculate_multi_acccount_multi_season_peak_rank()
        # time.sleep(0.5)  # Random sleep

        if summoner_profiles:
            return summoner_profiles
        else:
            return summoner_ign
    
    @staticmethod
    def identify_query_input(query):
        """
        [info] Analyzes and categorizes the input query type for appropriate processing
        
        Identifies query types: multisearch, single search, summoner IGN, or non-standard.
        Sets appropriate flags and extracts region information.
        
        [param] query: str - The input query to analyze
        
        [return] tuple: (query_list, summoner_profiles) for processing
        """
        multisearch_query_list = []
        summoner_profiles = []
        
        info_print("Identifying Query Type")
        
        # Region Assignment
        if "/euw" in query:
            error_print("EUW Region Not Supported!")
            sys.exit(1)
        elif "/na" in query:
            success_print("Region: NA")
        
        # Profile Type Assignment
        if "multisearch" in query:
            OPGGScraper.isProfileMultiSearch = True
            success_print("Multi-Search", header="PROFILE TYPE")
            multisearch_query_list, summoner_profiles = OPGGScraper.handle_multi_search(query)
        elif ("leagueofgraphs" in query) or ("u.gg" in query):
            OPGGScraper.isProfileNonStandard = True
            error_print("Non-Standard Profile", header="PROFILE TYPE")
            error_print("Non-Standard Profile Not Supported!")
            sys.exit(1)
        elif "op.gg/summoners" in query:
            OPGGScraper.isProfileSingleSearch = True
            success_print("Single Search", header="PROFILE TYPE")
        elif "#" in query: # could be a single IGN
            # MATCHA: count number of hashtags in the query for number of profiles
            OPGGScraper.isProfileSummonerIGN = True
            success_print("Summoner IGN", header="PROFILE TYPE")
        else: # non standard profile, handle in terminal
            OPGGScraper.isProfileNonStandard = True
            error_print("Non-Standard Profile", header="PROFILE TYPE")
            error_print("Non-Standard Profile Not Supported!")
            sys.exit(1)
        
        # return the query list if it is a multisearch query (multiple queries)
        if multisearch_query_list:
            return multisearch_query_list, summoner_profiles
        else:
            return [query], []
        
    @staticmethod
    def handle_query_input(query):
        """
        [info] Processes the identified query input and executes appropriate search method
        
        Handles different profile types: summoner IGN search, single profile, or multi-search.
        Navigates to appropriate pages and waits for content to load.
        
        [param] query: str - The query to process
        
        [return] str: Processed query or -1 on error
        """
        info_print("Processing Query Input")

        if OPGGScraper.isProfileSummonerIGN:
            isProfileHandled = False
            warning_print("Handling Profile Type: Summoner IGN...")

            while not isProfileHandled:
                IGN = query
                search_url = OPGGScraper.MAIN_WEBSITE # use existing URL

                try: 
                    OPGGScraper.DRIVER.get(search_url)

                    # Find the op.gg search box
                    search_box = OPGGScraper.DRIVER.find_element(By.NAME, 'search')

                    # enter the summoner IGN + enter
                    search_box.send_keys(IGN + Keys.RETURN)  # Send query and hit Enter

                    # Wait for the search results to load, via the top-tier class
                    warning_print("Waiting for Search Results to Load...")

                    status = OPGGScraper.wait_for_element_to_load(By.XPATH, "//*[@id='content-header']/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div/h1/div/span[1]")
                
                    if status == -1:
                        error_print("Search Results Not Found!")

                    success_print("Search Results Loaded!")
                    isProfileHandled = True
                except: 
                    error_print("Failed to Handle Profile Type: Summoner IGN")
                    error_print("Press <ENTER> to continue...")
                    input()
                    return -1

        elif OPGGScraper.isProfileSingleSearch:
            warning_print("Handling Profile Type: Single Search...")
            search_url = query
            OPGGScraper.DRIVER.get(search_url)  # Open the search URL directly

        elif OPGGScraper.isProfileNonStandard:
            error_print("NOT Handling Profile Type: Non-Standard Profile...")
            sys.exit()

        return query 
    
    @staticmethod
    def handle_multi_search(query):
        """
        [info] Processes multi-search queries to extract multiple player profiles
        
        Navigates to multi-search results and extracts individual summoner links and IGNs.
        Converts multi-search into list of single search queries.
        
        [param] query: str - The multi-search URL
        
        [return] tuple: (query_list, summoner_profiles) or (-1, -1) on error
        """
        query_list = []
        summoner_profiles = []
        
        # sanity check
        if not OPGGScraper.isProfileMultiSearch:
            error_print("Multi-Search Query Not Detected!")
            sys.exit()

        if OPGGScraper.DRIVER is None:
            OPGGScraper.DRIVER = OPGGScraper.get_web_driver()  # Initialize WebDriver
        
        # open the multisearch query link 
        OPGGScraper.DRIVER.get(query)

        # wait for the search results to load
        info_print("Chunking Multi-Search Profile")
        try: 
            OPGGScraper.wait_for_element_to_load(By.CLASS_NAME, 'multi-list')

            # identify multi-list container
            multi_list_container = OPGGScraper.DRIVER.find_element(By.CLASS_NAME, 'multi-list')
            success_print("Multi-Search Results Loaded!", header="STATUS")

            # identify the <li> child elements
            multi_list_items = multi_list_container.find_elements(By.TAG_NAME, 'li')

            # per <li> element, extract the class-name element of 'summoner-summary'
            counter = 1
            for item in multi_list_items:
                try: 
                    summoner_summary = item.find_element(By.CLASS_NAME, 'summoner-summary')
                except NoSuchElementException as e: # empty list profile (totally okay)
                    continue

                # find child element of class name 'summoner-name' (but handle specific exception if it doesn't exist)
                try: 
                    summoner_name = summoner_summary.find_element(By.CLASS_NAME, 'summoner-name')
                except NoSuchElementException as e: # empty list profile (totally okay)
                    continue

                # find the  <a> child element
                summoner_name_a = summoner_name.find_element(By.TAG_NAME, 'a')
                
                # find its href link & summoner ign 
                summoner_href = summoner_name_a.get_attribute('href')
                summoner_ign = (summoner_name_a.text).replace("\n", "")

                info_print(f"Extracting Summoner Info for Profile {counter}")
                success_print({summoner_ign}, header="SUMMONER IGN")
                success_print({summoner_href}, header="SUMMONER LINK")
                query_list.append(summoner_href)
                summoner_profiles.append(summoner_ign)
                counter += 1
        except Exception as e:
            error_print(f"Failed to Load Multi-Search Results: {e}")
            error_print("Press <ENTER> to continue...")
            input()
            return -1, -1

        OPGGScraper.isProfileMultiSearch = False
        OPGGScraper.isProfileSingleSearch = True # bc now we have a list of single search profiles

        return query_list, summoner_profiles
    
    @staticmethod
    def update_opgg_summoner_profile():
        """
        [info] Forces an update of the OP.GG summoner profile before data extraction
        
        Checks last update time and triggers profile refresh if needed.
        Ensures the most recent data is available for scraping.
        
        [return] int: 0 for success, -1 for failure
        """
        info_print("Force Updating Summoner OP.GG Profile")
        try:
            # Get the last update field and print it
            OPGGScraper.wait_for_element_to_load(By.CLASS_NAME, 'last-update')
            last_update_field = OPGGScraper.DRIVER.find_element(By.CLASS_NAME, 'last-update')
            content = last_update_field.text

            # Check if the last update field contains "Last Updated: "
            if "Last updated: " in content:
                warning_print(f"{content}")

                try: # try finding the update button on the screen + click it

                    # BUTTON STATES: IDLE, REQUEST, DISABLE
                    update_button = OPGGScraper.DRIVER.find_element(By.XPATH, "//*[contains(@class, 'IDLE') and contains(@class, 'css-1ki6o6m') and contains(@class, 'e17xj3f90')]")
                    update_button.click()

                    # wait for "update" to register
                    warning_print("Waiting for Update to Complete...")
                    # MATCHA: increase timeout to fully updates the profile for recent scouting
                    OPGGScraper.wait_for_element_to_load(By.XPATH, "//*[contains(@class, 'DISABLE') and contains(@class, 'css-1r09es5') and contains(@class, 'e17xj3f90')]")
                    success_print("Update Complete!")

                except Exception as e:
                    error_print(f"ERROR w/ Update Button Press: {e}")

                # Get the updated last update field and print it
                last_update_field = OPGGScraper.DRIVER.find_element(By.CLASS_NAME, 'last-update')
                warning_print(f"Next Update {last_update_field.text}")

            else: # updated within the last 2 minutes
                warning_print(f"Next Update: {content}")
            
            return 0 # success
        except Exception as e:
            error_print(f"Failed to Update Summoner Profile (last-update field not found): {e}")
            return -1 # failure
        
    @staticmethod
    def scrape_summoner_ign():
        """
        [info] Extracts the summoner IGN and tag from the current profile page
        
        Locates and extracts the summoner name and tag from the profile header.
        Cleans formatting and returns the complete summoner identifier.
        
        [return] str: Clean summoner IGN with tag, or -1 on error
        """
        info_print("Scraping Summoner IGN && Tag")
        # time.sleep(100)
        # OPGGScraper.wait_for_element_to_load(By.XPATH, "/html/body/div[5]/div[2]/div/div[1]/div/div[1]/ul/li[1]/a/span")
        # info_print("PageLoaded")
        # summoner_ign_header = OPGGScraper.DRIVER.find_element(By.XPATH, "/html/body/div[5]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div/h1/div/span[2]")
        try:
            # summoner_ign_header = OPGGScraper.DRIVER.find_element(By.XPATH, "/html/body/div[5]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div/h1/div/span[2]")
            summoner_ign_header = OPGGScraper.DRIVER.find_element(By.XPATH, "/html/body/div[5]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div/h1")
            summoner_ign = summoner_ign_header.text
            summoner_ign = summoner_ign.replace("\n", "")
            # time.sleep(15)  # Random sleep
            success_print(f"Summoner IGN: {summoner_ign}")
            return summoner_ign
        except Exception as e:
            error_print(f"Failed to Scrape Summoner IGN: {e}")
            error_print(f"Press <ENTER> to continue...")
            input()
            return -1
        # continue on from Line 278 - Handle Query Input

        