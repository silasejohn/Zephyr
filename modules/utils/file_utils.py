import json

# save json to a json file
def save_json_to_file(json_data, file_name):
    with open(file_name, 'w') as f:
        json.dump(json_data, f, indent=4)

# load json from a json file
def load_json_from_file(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data