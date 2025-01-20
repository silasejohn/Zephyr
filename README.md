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

Features: 
- support for cross-folder imports via customized sys_path updates (handled automatically wrt to project directory)
- API Queue System: graceful handling of API calls, automatic retry of failed calls, and managing rate-limited requests
- retry mechanism: exponential backoff & queue system 
    - [1] Queue System: all api calls are added to a queue
    - [2] Retry Mechanism: retry failed calls with 5XX (server issue) response, MAX_RETRY_LIMIT, and exponential backoff
    - [3] Rate Limiting: throttle requests to adhere to the Riot API's rate limits
    - [4] Logging: log each API request & response, including errors


TODO: 
- riot API exploration
- API Queue System (refer to Chat)
    - retry_attempts should be a config env MAX_RETRY_ATTEMPTS
    - logging
    - craft() calls should return an api_id. process() calls shouldn't execute until api_id returns "true"?
- average game time for teams 
- change params to accomodate optional params (if one is specified, then add to the param dict, else don't)
- Logic within your application should fail gracefully based the response code alone, and should not rely on the response body.
    - https://developer.riotgames.com/docs/portal#:~:text=500%20(Internal%20Server%20Error)%20This,because%20of%20an%20unknown%20reason.
- Respect the rate limit for your Tournament API Key and implement logic that considers the headers returned from a 429 Rate Limit Exceeded response.
- database integration (caching results)
- connect to google spreadsheet for auto-outputting data
- dynamically generate spreadsheet_info.json
- Output everything at the end into google spreadsheets directly for output
- for matchDTO, see if there's a way to use the **args thingy to directly import a dict into the MatchDTO class or only identify useful information / heads (like pick / bans) and see if we can partially upload

Zephyr API Key
- 20 requests every 1 seconds
- 100 requests every 2 minutes
- Individual Request Rates per API Call? (check ZephyrRateLimits.json)

## Identify Past Peak Ranks??
To determine past rank peaks using the Riot API, you need to first retrieve a summoner's current information using the "Get Summoner By Account" endpoint, which will provide their summoner ID, then use that ID to access their match history through the "Get Matchlist" endpoint, parsing each match to identify their rank at the time of play, and finally, analyze this data to identify their highest achieved rank across a specific period of time. 
- need to create rank split divides and maintain a "max" for each split
- very necessary to simply cache the match histories per each player imo



QUEUE TYPES
Unranked
    RANKED_SOLO_5x5 (valid)
    RANKED_TEAM_5x5
Ranked Solo/Duo
    RANKED_SOLO_5x5 (valid)
Ranked Team 5x5
    RANKED_TEAM_5x5
Ranked Flex
    RANKED_FLEX_SR  (valid)


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


SAMPLE RIOT API PYTHON APP - https://github.com/RiotGames/developer-relations/blob/main/sample_apps/rso_sample_apps/python/main.py
RIOT GAMES API DEEP DIVE - https://technology.riotgames.com/news/riot-games-api-deep-dive

API client typically encompasses the logic needed to interact with specific endpoints, handle requests, and process responses
Craft Functions: These functions construct the request payloads, URLs, headers, and other parameters needed to make API calls.
Process Functions: These functions handle the responses from the API, including parsing data, handling errors, and executing business logic based on the API's responses.

you need a __init__.py with a update_sys_path() function if you call classes / funcs from other nested folders 



<sub><sup>Zephyr is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc</sup></sub>