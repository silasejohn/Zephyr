###############
### IMPORTS ###
###############

# global imports
import os, json

# local imports
from . import update_sys_path
update_sys_path(True)
from modules.api_clients.riot_client.services.account_v1 import ACCOUNT_V1
from models.account_dto import AccountDTO

def get_match_participants():
    """
    [info] Extract and return participants from match data. This function is intended to process match DTO data and retrieve participant information. Currently not implemented - functionality should potentially be moved to match DTO .py file.
    
    [return] None - function not yet implemented
    """
    # probably should handle this in match DTO .py file
    pass