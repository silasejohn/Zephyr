import json
import dotenv
import os

# CONFIG GOOGLE SHEETS output sheet
def get_spreadsheet_config():
    with open("config/spreadsheet_info.json") as f:
        return json.load(f)
    
# config RIOT API Environment Variables
def get_riot_api_config(param: str = None):
    dotenv.load_dotenv("config/api.env")
    if param:
        return os.getenv(param)
    else:
        return f"No parameter found for {param}"
