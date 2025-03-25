

## REQUIREMENTS
> Point Value - dependant on various characteristics 
> Multi-Player PV (3, 8) Cutoff similar to GCS

## Point Value Characteristics 
(1) SoloQ Ranking (SQR)
- Current Rank
- Prev Split Rank
- Peak Rank (over 2 years)
- Average Rank (over 2 years) 
- (if time) Top % Placing ... 
- (if time) # of games played each season 
(2) Champ Mastery (CM)
- No. of Champs @ each Champ Mastery Level
- No. of Champs above a certain Mastery Level threshold
- No. of Games per Champ (per role, in ranked vs norms) 
(3) Perceived InHouse Skill Score (PISS) 
- In House MMR
- In House WR
... outlined to Kris, GP, Gepetto

## Plan of Action
(1) LEPL Form Response Processing / Cleaning
... input: form response spreadsheet
... output: running "conglomerate" of cleaned form response (periodically updated based on changing input) spreadsheet 
(2) LEPL Player Scouting / Data Scraping
... input: cleaned form response data 
... output: lepl_roster.json (static info) + folder per person (champ mastery) + lepl_roster.csv (stats)
(3) LEPL PV Generation
... input: lepl_roster.json ... etc
... output: rank scores into lepl_roster.json 