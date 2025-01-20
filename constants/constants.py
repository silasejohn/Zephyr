###############
### Imports ###
###############

# local imports
from __init__ import update_sys_path
update_sys_path()
from modules.utils.file_utils import save_json_to_file, load_json_from_file

class Constants:
    def __init__(self):
        self.champion_constants = load_json_from_file("constants/champions.json")
        self.gameType_constants = load_json_from_file("constants/gameTypes.json")
        self.maps_constants = load_json_from_file("constants/maps.json")
        self.queue_constants = load_json_from_file("constants/queues.json")
        self.responseCode_constants = load_json_from_file("constants/responseCodes.json")
        self.zephyrRateLimit_constants = load_json_from_file("constants/zephyrRateLimits.json")
    
    # get champion name from champion id
    def get_champion_name(self, champion_id):
        champion_keys = self.champion_constants['data'].keys()
        for champ in champion_keys:
            if self.champion_constants['data'][champ]['key'] == str(champion_id):
                return self.champion_constants['data'][champ]['id']
        else:
            return -1

    