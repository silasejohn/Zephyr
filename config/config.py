import json

# import config json file 
def get_spreadsheet_config():
    with open("config/spreadsheet_info.json") as f:
        return json.load(f)
    
