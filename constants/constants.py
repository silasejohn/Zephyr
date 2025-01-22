###############
### Imports ###
###############

# local imports
from __init__ import update_sys_path
update_sys_path()
from modules.utils.file_utils import save_json_to_file, load_json_from_file

class Constants:
    def __init__(self):
        self.CHAMPION_CONSTANTS = load_json_from_file("constants/champions.json")
        self.GAME_TYPES = load_json_from_file("constants/gameTypes.json")
        self.MAP_TYPES = load_json_from_file("constants/maps.json")
        self.QUEUE_TYPES = load_json_from_file("constants/queues.json")
        self.RESPONSE_CODES = load_json_from_file("constants/responseCodes.json")
        self.ZEPHYR_RATE_LIMITS = load_json_from_file("constants/zephyrRateLimits.json")
        self.GCS_TEAMS = load_json_from_file("constants/gcsTeams.json")
    
    # get champion name from champion id
    def get_champion_name(self, champion_id):
        champion_keys = self.CHAMPION_CONSTANTS['data'].keys()
        for champ in champion_keys:
            if self.CHAMPION_CONSTANTS['data'][champ]['key'] == str(champion_id):
                return self.CHAMPION_CONSTANTS['data'][champ]['id']
        else:
            return -1

    def update_original_json(self, constant_str: str):
        match constant_str:
            case "CHAMPION_CONSTANTS":
                save_json_to_file(self.CHAMPION_CONSTANTS, "constants/champions.json")
                return
            case "GAME_TYPES":
                save_json_to_file(self.GAME_TYPES, "constants/gameTypes.json")
                return
            case "MAP_TYPES":
                save_json_to_file(self.MAP_TYPES, "constants/maps.json")
                return 
            case "QUEUE_TYPES":
                save_json_to_file(self.QUEUE_TYPES, "constants/queues.json")
                return 
            case "RESPONSE_CODES":
                save_json_to_file(self.RESPONSE_CODES, "constants/responseCodes.json")
                return
            case "ZEPHYR_RATE_LIMITS":
                save_json_to_file(self.ZEPHYR_RATE_LIMITS, "constants/zephyrRateLimits.json")
                return
            case "GCS_TEAMS":
                save_json_to_file(self.GCS_TEAMS, "constants/gcsTeams.json")
                return 
    