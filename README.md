# Zephyr

*True to its name, Zephyr delivers subtle yet powerful insights that can shape the outcome of your scouting & tournament draft. While it won’t guarantee victory, its meticulous analysis of opponents provides the strategic advantage needed to tip the balance in your favor, setting the stage for success before your match even starts*

## Project Structure
```
project_root/
│
├── data/                       # data storage
│   ├── raw/                    # (raw) data
│   └── synthesized/            # (processed) data
│
├── scripts/                    # python scripts
│   ├── __init__.py
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── opgg_profile_scraper.py          # 
│   │   └── riot_api_client.py               # For API interactions
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── data_processor.py   # Handles data processing and transformations
│   │   └── output_formatter.py # Formats data for output (e.g., CSV, JSON)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_manager.py     # Manages reading/writing CSV and JSON
│       └── helpers.py          # Miscellaneous utility functions
│
├── notebooks/                  # Jupyter notebooks for exploratory analysis
│
├── config/                     # Configuration files
│   └── settings.py             # Configuration for scraping, APIs, paths
│
├── tests/                      # Test cases for your modules
│
├── .gitignore
├── README.md
└── requirements.txt            # Dependencies for the project

```

https://developers.google.com/sheets/api/quickstart/python

[Activate Virtual Environment] `source hw2-env/bin/activate`

[Changing Scope Locally] Delete `config/token.json`

[Configure Run Button to Virtual Env] CMD + SHIFT + P ~> Select Appropriate Interpreter (auto configures run button)

[RESET Riot API Key every 24 hours] Response Codes: Note that our APIs return only non-empty values to save on bandwidth. Zero is considered an empty value, as well as empty strings, empty lists, and nulls. Any numeric field that isn't returned can be assumed to be 0 (or null as you prefer). Any list field that isn't returned can be assumed to be an empty list or null. Any String field that isn't returned can be assumed to be empty string or null.
- always read the "status" ~> response code first before the response 
- https://developer.riotgames.com/docs/portal
- https://developer.riotgames.com/docs/lol 
- Route via na1.api.riotgames.com (platform) or americas.api.riotgames.com (region)
- use data dragon for champ pics 
 
TODO: 
- finish cross packaging on python within double nested folders
- riot API


# API STUFF
`SUMMONER-V4` 
- [INPUT] player’s in-game name (summoner name)
- [OUTPUT] profile data

`MATCH-V5` 
- [INPUT] player puuid
- [OUTPUT] match ids from last 20 games played

`MATCH-V5` 
- [INPUT] match id
- [OUTPUT] match information

DTO = Data Transfer Object (in API world)
Riot ID = <IGN><TAG>
- ex. dont ever stop#NA1


<sub><sup>Zephyr is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc</sup></sub>