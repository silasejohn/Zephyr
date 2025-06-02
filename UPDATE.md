1. [constants/gcsTeams.json] Update <team_id> Team Rosters Info && Draft Analysis Spreadsheet
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


-----
* add playerID, op_gg link and log_link, gcs_link, gcs_team_link

* flag for re-run if any profile has a problem, store, and (auto)ReRun
1. (per team-id roster) Update [constants/gcs_s2_teams.json] w/ Player OP.GGs, rank_score, player_pos
- potentially pull roles from GCSLEAGUE
2. Run "Update Roster Riot MetaData" function
- (first time) player_puuid, player_encrypted_summoner_id, player_encrypted_account_id 
- (if player_puuid exists) check update player_riot_id
3. Run "Update Roster Rank MetaData" (on team-id specific mode)
- (if no player_log_link) generate LOG URL via Riot ID
- (if no player_opgg_link) generate OP.GG URL via Riot ID
- (if no peak_rank) PULL PEAK RANK via LOG 
- PULL CURRENT RANK via OPGG ... update peak_rank if needed
4. Run "Update Roster Champion Data" 
- (first time, no champ pool csv) Create Rewind.Lol profile ... max 5 queue! 
- (else) Update rewind.lol profile... max 5 queue!
- Download Updated Past 2 years Champ Pool + Role Distribution (don't need to focus on player_pos)
- PULL recent champs via OP.GG or LOG or RIOT API! (past week roles + champs)
- PULL tourney champs via GCSLEAGUE (all played roles + champs)
5. Display on Google Spreadsheets! (uniform formatting)
6. AI-Based Live Draft Tool
- Generate Point-Value System for Champ Priority (recent tourney pick by X, recently played by X, most played by X in total history?, for a role that X plays the most?, check messenger i wrote some notes, but do process of elimination and give a priority list of potential(player - champ - role) with a certainty percentage)
- Live Processes Draft Input Picks made by either team 
- Shows Potential for each champ by Enemy Team
- Shows Available Picks for each champ by Ego Team (can custom add some champ picks)
- FEARLESS CAPABILITY (cancels out champs already played / picked) 
- CLICK ON ENEMY PROFILE - display remaining champs per player / role with a likelihood of being played
- DISPLAYS NICE FORMATTING (champ icons, champ names, games played, color coded text based on WR, games played etc)
- 3 Time Frames (last week, last month, last 2 years) ... prob use riot champ access per player profile for this to be accurate

1st thing: if a champ is picked by enemy, who is playing it in what role likelihood? 
2nd thing: given X roles left, per role, what is most likely available to be chosen given on a priority system (accounting for fearless)


