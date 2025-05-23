## This script is used to access the champion pool of a team and its members

##########################
### Import Statements ####
##########################

# local imporst
from __init__ import update_sys_path
update_sys_path()

# global imports
from modules.scrapers.rewind_lol_scraper import LeagueChampScraper
position_list = ["top", "jng", "mid", "bot", "sup"]
##########################

tournament_id = "GCS_Season_2"
team_id = "WOW"
update_rewind_profile = False

#### TEAM FETCH ###
# input_riot_ids, input_team_positions = LeagueChampScraper.retrieve_team_roster(team_id)

# input_riot_ids = [["BoyHoleBuccaneer#Boom", "GourmetCookies#NA1"]]
# input_team_positions = [["sup"]]

input_riot_ids = [["Shayden#Coney"], ["Agu#CN1"], ["PingSpam#NA1"], ["Happiercat477#NA1", "Katamine#KxC", "ErisTheExile#NA1"], ["AcidStep#NA1", "StepAcid#NA1"], ["waterslulluby#NA1", "awesomeguytx#NA1"], ["Ferestric#MAW"], ["0beron Vortigern#NA1"], ["bergamot#sweet"]]
input_team_positions = [["jng", "sup", "top"], ["top", "sup"], ["bot", "mid", "sup"], ["mid", "top"], ["mid", "jng"], ["bot", "sup"], ["bot", "sup"], ["top", "mid"], ["jng", "sup", "mid"]]

# input("Press Enter to continue...")

if update_rewind_profile:
    LeagueChampScraper.update_team_champ_history(tournament_id, team_id, input_riot_ids, run_update = False)
LeagueChampScraper.access_team_champ_pool(tournament_id, team_id, input_riot_ids, input_team_positions)

### INDIVIDUAL FETCH ###
# ign = "James Sunderland#KLLR7"
# pos = "bot" # bot
# LeagueChampScraper.access_player_champ_pool(team_id=None, r_ign=ign, r_pos=pos)
# # setup profile from scratch (w/o team_id) and fetch ... put into a non-team-if based folder
