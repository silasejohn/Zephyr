
from selenium.webdriver.common.by import By        
from collections import Counter                         # for locating elements BY specific types (e.g. ID, NAME, etc.)
import sys

# local imports
from __init__ import update_sys_path
update_sys_path()

# unique print inports
from modules.utils.color_utils import warning_print, error_print, info_print, success_print
from modules.scrapers.gcs_league_scraper import GCSLeagueScraper

#####################################

setup = False
TEAM_NAME = "WRAP GODS"  # Team ID for GCS League Season 2
GCS_TEAM_PAGE = ""

#####################################

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


# setup the GCS_LEAGUE website for scraping as needed
if not setup:
    GCSLeagueScraper.set_up_gcs_league()
    setup = True

    # transform TEAM_NAME into Camel Case
    TEAM_NAME = TEAM_NAME.title()
    info_print(f"Transformed TEAM_NAME to Camel Case: {TEAM_NAME}")

# XPATH to LIST of Teams: /html/body/main/div/div[3]/ol
GCSLeagueScraper.wait_for_element_to_load(
    By.XPATH, 
    "/html/body/main/div/div[3]/ol",
    timeout=10
)

team_list_container = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "/html/body/main/div/div[3]/ol")
list_of_teams_and_scores = team_list_container.text

# find list of teams
team_pool_list = team_list_container.find_elements(By.TAG_NAME, "li")

# find containers for diff pools of teams
pool_1_team_list_container = team_pool_list[0]  # ALL Pool 1 Teams 
pool_1_container_text = pool_1_team_list_container.text
pool_2_team_list_container = team_pool_list[9]  # ALL Pool 2 Teams
pool_2_container_text = pool_2_team_list_container.text

# split by '\n' and each entry is an array value
pool_1_team_list = pool_1_container_text.split('\n')
pool_2_team_list = pool_2_container_text.split('\n')

# combine both lists into a single list
both_pools_team_list = pool_1_team_list + pool_2_team_list

# chunk out the team scores from the team names
both_pools_team_list = [
    team if "Pool" in team else ' '.join(team.split()[:-1]) 
    for team in both_pools_team_list
]

# return list index of TEAM_NAME
team_index = both_pools_team_list.index(TEAM_NAME) if TEAM_NAME in both_pools_team_list else -1

# acccess the team information URL 
if team_index == -1:
    error_print(f"Team '{TEAM_NAME}' not found in the list of teams.")
    sys.exit(1)  # Exit the script if the team is not found
else:
    team_info_container = team_pool_list[team_index]
    GCS_TEAM_PAGE = team_info_container.find_element(By.TAG_NAME, "a").get_attribute("href")
    success_print(f"Found team '{TEAM_NAME}' at index {team_index}.")
    info_print(f"Team HREF: {GCS_TEAM_PAGE}")
    GCSLeagueScraper.DRIVER.get(GCS_TEAM_PAGE)

# XPATH: TEAM PLAYER IDs - /html/body/main/div/div/div[1]
GCSLeagueScraper.wait_for_element_to_load(
    By.XPATH, 
    "/html/body/main/div/div/div[1]/div/ul",
    timeout=10
)

# find the container for the list of players
player_list_container = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "/html/body/main/div/div/div[1]/div/ul")

# list of players
player_list = player_list_container.find_elements(By.TAG_NAME, "li")

# iterate through players, scrape their player_temp_id, their declared positions, and their href links
player_dict_temp = {}
player_dict = {}  # final player dictionary with discord tags as keys

# iterate through each player in the player list and extract some player metadata
for player in player_list:
    # find the <a> tag within the <li> tag
    player_a_tag = player.find_element(By.TAG_NAME, "a")
    player_href = player_a_tag.get_attribute("href")  # Player HREF
    # find the <div> tag within the <a> tag
    player_div_tag = player_a_tag.find_element(By.TAG_NAME, "div")

    player_h3_tag = player_div_tag.find_element(By.TAG_NAME, "h3")
    player_p_tag = player_div_tag.find_element(By.TAG_NAME, "p")

    player_temp_id = player_h3_tag.text.strip()  # Player Temp ID
    player_declared_positions = player_p_tag.text.split("/")  # split by comma and space

    player_declared_positions = [
        standardize_position(pos.strip()) for pos in player_declared_positions
        if standardize_position(pos.strip()) != -1
    ]  # standardize positions and filter out invalid ones
    player_declared_positions = list(set(player_declared_positions))  # remove duplicates

    print(f"Player Temp ID: {player_temp_id}")
    print(f"Player Declared Positions: {player_declared_positions}")
    print(f"Player HREF: {player_href}")

    # store in player dictionary by player discord tag
    player_dict_temp[player_temp_id] = {
        "player_temp_id": player_temp_id,
        "declared_positions": player_declared_positions,
        "href": player_href
    }

# store proper player information in player_dict with discord tags as keys
for player_info in player_dict_temp.values():
    GCSLeagueScraper.DRIVER.get(player_info['href'])

    GCSLeagueScraper.wait_for_element_to_load(
        By.XPATH, 
        "/html/body/main/div/header/ul/span",
        timeout=10
    )
    discord_tag = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "/html/body/main/div/header/ul/span").text.strip()

    # replace the player_temp_id key in the player_dict with the discord_tag
    if discord_tag not in player_dict:
        player_dict[discord_tag] = {
            "player_temp_id": player_info['player_temp_id'],
            "declared_positions": player_info['declared_positions'],
            "href": player_info['href']
        }

    # click the "update" button" 
    # XPATH: /html/body/main/div/div/div[1]/div/form/p/input
    update_button = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "/html/body/main/div/div/div[1]/div/form/p/input")
    if update_button.is_displayed():
        update_button.click()
        info_print(f"Clicked 'Update' button for player {discord_tag}.")
    else:
        warning_print(f"'Update' button not found for player {discord_tag}.")
    
    # buffer for 1s
    GCSLeagueScraper.buffer(1)

    # pull their tournament match history, wait for it to load
    GCSLeagueScraper.wait_for_element_to_load(
        By.XPATH, 
        "/html/body/main/div/div/div[2]/div/ol",
        timeout=10
    )

    player_tourney_match_history_container = GCSLeagueScraper.DRIVER.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/ol")
    player_tourney_match_history_list = player_tourney_match_history_container.find_elements(By.TAG_NAME, "li")
    
    # keep track of player champion names and positions played (but both are related per match)  
    player_pos_champ_dict = {}  # dictionary to store champion names and positions played

    # iterate through each match & player match info
    match_counter = 0
    for match_container in player_tourney_match_history_list:
        match_container_a_tag = match_container.find_element(By.TAG_NAME, "a")
        match_champ_name_container = match_container_a_tag.find_element(By.TAG_NAME, "img").get_attribute("alt").strip()
        match_champ_name = ' '.join(match_champ_name_container.split()[:-1]) # keep everything but the last word
        match_container_div_tag = match_container_a_tag.find_element(By.TAG_NAME, "div")
        match_container_p_tag_list = match_container_div_tag.find_elements(By.TAG_NAME, "p")
        match_position = match_container_p_tag_list[3].text.strip().replace("Position: ", "")  # Player Position
        match_position = standardize_position(match_position)  # standardize the position name
        if match_position == -1:
            error_print(f"Invalid position '{match_position}' for champion '{match_champ_name}'. Skipping...")
            input("Press Enter to continue...")
            continue

        # store the champion name and position played   
        player_pos_champ_dict[match_counter] = f"{match_position}_{match_champ_name}"
        match_counter += 1
        print(f"Champion Name: {match_champ_name}")
        print(f"Player Position: {match_position}")

    # store the player_pos_champ_dict in the player_info dictionary
    player_dict[discord_tag]['player_pos_champ_history'] = player_pos_champ_dict

print("\nPlayer Dictionary:")
for discord_tag, player_info in player_dict.items():
    print(f"Discord Tag: {discord_tag}")
    print(f"\tPlayer Temp ID: {player_info['player_temp_id']}")
    print(f"\tDeclared Positions: {', '.join(player_info['declared_positions'])}")
    print(f"\tHREF: {player_info['href']}")

    champ_list = []
    pos_list = []

    # do some aggregate stats (how much of each champ played, how many of each position played)
    print(player_info)
    for pos_champ in player_info['player_pos_champ_history'].values():
        pos, champ = pos_champ.split("_")
        champ_list.append(champ)
        pos_list.append(pos)
        
    champion_count = Counter(champ_list)
    position_count = Counter(pos_list)
    # sort the counts decreasing in value
    champion_count = dict(sorted(champion_count.items(), key=lambda item: item[1], reverse=True))
    position_count = dict(sorted(position_count.items(), key=lambda item: item[1], reverse=True))

    print("\tChampion Count:\t", end="")
    for champ, count in champion_count.items():
        print(f"{champ} ({count})", end=", ")
    print("\n\tPosition Count:\t", end="")
    for pos, count in position_count.items():
        print(f"{pos} ({count})", end=", ")  
    print("\n\n")  

    # MATCHA: TODO if in last X games (variable based on tourney, give a x2 bonus count to those champ played)
    # MATCHA: TODO ... upload this info to spreadsheet
    # MATCHA: create json for every team with new fields!

input("Press Enter to continue...")

GCSLeagueScraper.close()


