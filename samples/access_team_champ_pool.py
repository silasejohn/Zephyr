## This script is used to access the champion pool of a team and its members

##########################
### Import Statements ####
##########################

# local imporst
from __init__ import update_sys_path
update_sys_path()

# global imports
from modules.scrapers.rewind_lol_scraper import LeagueChampScraper

##########################

position_list = ["top", "jng", "mid", "bot", "sup"]

team_id = "07"

#### TEAM FETCH ###
input_riot_ids, input_team_positions = LeagueChampScraper.retrieve_team_roster(team_id)
LeagueChampScraper.update_team_champ_history(team_id, input_riot_ids, run_update = False)
LeagueChampScraper.access_team_champ_pool(team_id, input_riot_ids, input_team_positions)

### INDIVIDUAL FETCH ###
# ign = "James Sunderland#KLLR7"
# pos = "bot" # bot
# LeagueChampScraper.access_player_champ_pool(team_id=None, r_ign=ign, r_pos=pos)
# # setup profile from scratch (w/o team_id) and fetch ... put into a non-team-if based folder

