1. Add Basic Info to gcsTeams.json
2. craft_team_rosters.py to generate <team_id>.json (updates puuids, riot ids, etc)
3. display basic roster info to NEW google spreadsheet via api calls
4. display past drafts on google spreadsheet via api calls
4. display champion mastery on google spreadsheet via api calls

1. Update GCS_tourney_match_overview_week{x}.json for match outcomes
2. Run riot_match_v5_example.py to pull all the json files of the custom games
3. parse_custom_tourney_json.py for analysis of the custom tournament match data