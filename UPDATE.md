1. [constants/gcsTeams.json] Update <team_id> Team Rosters Info
2. [craft_team_rosters.py] Change <team_id> and generate <team_id>.json (updates puuids, riot ids, etc)
3. Update rewind.lol profiles manually for all profiles on team
4. [access_team_champ_pool.py] change <team_id> and retrieve all known information

# ... do a role priority breakdown by role for everyone on a team...
# ... auto create profile on rewind.lol if not exist && auto update profile past a certain date (limit 5 for rate limiting)
# ... do op.gg scraping for champs played in last 30 days (recent match history)
# ... google spreadsheeet api calls to display directly on the sheets (determine format first)
# ... custom game drafts analysis (pick their past picks, roles, add to json for edits, add rosters / counters pick to the team rostres)
# ... pull champ mastery of champs as well for 3rd view on champs played

3. display basic roster info to NEW google spreadsheet via api calls
4. display past drafts on google spreadsheet via api calls
4. display champion mastery on google spreadsheet via api calls

1. Update GCS_tourney_match_overview_week{x}.json for match outcomes
2. Run riot_match_v5_example.py to pull all the json files of the custom games
3. parse_custom_tourney_json.py for analysis of the custom tournament match data