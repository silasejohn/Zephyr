###############
### IMPORTS ###
###############

# global imports
import os, json

# local imports
from __init__ import update_sys_path
update_sys_path(True)
from modules.api_clients.riot_client.services.account_v1 import ACCOUNT_V1
from models.account_dto import AccountDTO

def get_match_participants():
    # probably should handle this in match DTO .py file
    pass