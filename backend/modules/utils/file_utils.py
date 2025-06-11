import json

def save_json_to_file(json_data: dict, file_name: str) -> None:
    """
    [info] Save JSON data to a file
    [param] json_data: Dictionary or JSON serializable data to save
    [param] file_name: Path to the output file
    [return] None
    """
    with open(file_name, 'w') as f:
        json.dump(json_data, f, indent=4)

def load_json_from_file(file_name: str) -> dict:
    """
    [info] Load JSON data from a file
    [param] file_name: Path to the JSON file to load
    [return] Dictionary containing the loaded JSON data
    """
    with open(file_name) as f:
        data = json.load(f)
    return data