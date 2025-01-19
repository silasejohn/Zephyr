import time, datetime, json
from __init__ import update_sys_path

update_sys_path()

# given a MM, DD, YYYY, return the epoch timestamp
def get_epoch_timestamp(month, day, year):
    return int(time.mktime(datetime.datetime(year, month, day).timetuple()))

# get current time in epoch timestamp
def get_current_epoch_timestamp():
    return int(time.time())

# save json to a json file
def save_json_to_file(json_data, file_name):
    with open(file_name, 'w') as f:
        json.dump(json_data, f, indent=4)