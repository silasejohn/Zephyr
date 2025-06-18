## This script is used to access the champion pool of a team and its members

##########################
### Import Statements ####
##########################

# local imports
from __init__ import update_sys_path
update_sys_path()

# global imports
import json
from modules.scrapers.rewind_lol_scraper import LeagueChampScraper
from modules.scrapers.enhanced_rewind_scraper import EnhancedLeagueChampScraper
position_list = ["top", "jng", "mid", "bot", "sup"]
##########################

tournament_id = "GCS_Season_2"
team_id = "ZOOM"
update_rewind_profile = True

#### TEAM FETCH ###
# input_riot_ids, input_team_positions = LeagueChampScraper.retrieve_team_roster(team_id)

# input_riot_ids = [["BoyHoleBuccaneer#Boom", "GourmetCookies#NA1"]]
# input_team_positions = [["sup"]]

def load_team_data_from_json(team_id):
    """
    Dynamically load team roster and positions from JSON file
    Returns: (input_riot_ids, input_team_positions)
    """
    # Position mapping from JSON format to accepted format
    position_mapping = {
        "TOP": "top",
        "JGL": "jng", 
        "MID": "mid",
        "BOT": "bot",
        "SUP": "sup"
    }
    
    # Load team data from JSON
    TEAM_DATA_JSON = f"data/processed/gcs_s2_tourney_scout_info/{team_id}.json"
    with open(TEAM_DATA_JSON, 'r') as f:
        team_data = json.load(f)
    
    input_riot_ids = []
    input_team_positions = []
    
    for player_discord, player_info in team_data.items():
        # Get player IGNs (accounts)
        player_igns = player_info["player_igns"]
        input_riot_ids.append(player_igns)
        
        # Get all possible positions for this player
        declared_positions = player_info.get("declared_positions", [])
        tourney_positions = list(player_info.get("tourney_positions_played_count", {}).keys())
        
        # Combine positions and map to correct format
        all_positions_raw = declared_positions + tourney_positions
        mapped_positions = []
        for pos in all_positions_raw:
            if pos in position_mapping:
                mapped_pos = position_mapping[pos]
                if mapped_pos in position_list and mapped_pos not in mapped_positions:
                    mapped_positions.append(mapped_pos)
        
        input_team_positions.append(mapped_positions)
    
    return input_riot_ids, input_team_positions

# Load team data dynamically
input_riot_ids, input_team_positions = load_team_data_from_json(team_id)

# Generated lists for ZOOM team:
# input_riot_ids = [['Boom#NYC', 'Boom v2#NA1', 'BooM on WeeD#NA1'], ['TouchVigor#NA1', 'Badxi#NA1'], ['Preston the Celt#NA1'], ['Tate#Pog'], ['Jimmus Thiccus#NA1'], ['Lurca#Lurca'], ['thefunniman#NA1', 'Nintendofan4ever#rider'], ['Bumii#NA1'], ['glåzza#NA1']]
# input_team_positions = [['bot', 'sup'], ['jgl', 'top'], ['bot', 'mid'], ['bot', 'mid'], ['mid', 'sup'], ['bot', 'mid', 'sup'], ['bot', 'sup'], ['bot', 'top'], ['bot', 'top']]

# input_riot_ids = [["Haumea#GCS", "Ha Yuri Zahard#T0G"]]
# input_team_positions = [["mid", "bot"]]
# input("Press Enter to continue...")

if update_rewind_profile:
    # Original version (commented out)
    # LeagueChampScraper.update_team_champ_history(tournament_id, team_id, input_riot_ids, run_update = False)
    
    # Enhanced version with auto-creation and intelligent rate limiting
    EnhancedLeagueChampScraper.auto_update_team_champ_history(tournament_id, team_id, input_riot_ids, run_update=True, max_retries=2)
LeagueChampScraper.access_team_champ_pool(tournament_id, team_id, input_riot_ids, input_team_positions)

### INDIVIDUAL FETCH ###
# ign = "James Sunderland#KLLR7"
# pos = "bot" # bot
# LeagueChampScraper.access_player_champ_pool(team_id=None, r_ign=ign, r_pos=pos)
# # setup profile from scratch (w/o team_id) and fetch ... put into a non-team-if based folder
