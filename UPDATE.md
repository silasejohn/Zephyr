1. [constants/gcsTeams.json] Update <team_id> Team Rosters Info
2. [craft_team_rosters.py] Change <team_id> and generate <team_id>.json (updates puuids, riot ids, etc)
3. Update rewind.lol profiles manually for all profiles on team
4. [rewind_lol_scraper.py] change <team_id> and scrape all known champ information
5. [access_team_champ_pool.py] change <team_id> and retrieve all known information

3. display basic roster info to NEW google spreadsheet via api calls
4. display past drafts on google spreadsheet via api calls
4. display champion mastery on google spreadsheet via api calls

1. Update GCS_tourney_match_overview_week{x}.json for match outcomes
2. Run riot_match_v5_example.py to pull all the json files of the custom games
3. parse_custom_tourney_json.py for analysis of the custom tournament match data