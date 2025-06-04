### Global Imports
import sys

### Local Imports
from __init__ import update_sys_path
update_sys_path()
from modules.api_clients.google_client.google_spreadsheet_api import SPREADSHEET_OPS
from modules.utils.color_utils import warning_print, error_print, info_print, success_print

# (1) assign scopes (READ_SCOPE or WRITE_SCOPE)
# ... if change scope, delete config/token.json and re-run the script
# (2) set proper spreadsheet and sheet ID (SAMPLE_SPREADSHEET_ID, SAMPLE_SHEET_NAME, SAMPLE_SHEET_RANGE)

#########################
### TOKENS / SECURITY ###
#########################
# [token.json] stores the user's access and refresh tokens
# ... created automatically when authorization flow completes for the first time

##############################
### SPREADSHEET / SHEET ID ###
##############################
SPREADSHEET_ID = "1uvQafCH4xmiKDgW0lE84AvL1x5n385MU2bIYEaTTR1A"
  # ... get this from the URL of the Google Sheet
TEAM_ID = "WG"  # Team ID 
TEAM_NAME = "Wrap Gods"  # Team Name 

def main():  

  # Initialize the Google Sheets API client
  SPREADSHEET_OPS.initialize("WRITE", SPREADSHEET_ID)

  # Delete Sheet for Team WG
  SPREADSHEET_OPS.delete_sheet("[WG] Wrap Gods")  # delete the sheet for the team if it exists

  # Create Sheet for TEAM WG
  SHEET_NAME = SPREADSHEET_OPS.create_sheet_for_team(TEAM_ID, TEAM_NAME)  # create a new sheet for the team

  # Edit a cell in the newly created sheet
  SPREADSHEET_OPS.edit_cell(SHEET_NAME, "C1", "C1 Cell Testing")  # edit the cell C1 to "TESTING2"
  sys.exit(0)  # exit the script after editing the cell

  input("Created New Sheet, Edited Cell - [ENTER] to continue...")  # wait for user input to continue

  # Call the Sheets API to get the text data snapshot of the sheet
  sheet_snapshot = SPREADSHEET_OPS.get_sheet_snapshot_basic(TEAM_ID, "B2:I")
  ## MATCHA - cache a local copy of the list of lists for sheet snapshot in sheet_info dict when this command is run
  SPREADSHEET_OPS.print_sheet_snapshot(sheet_snapshot)

  success_print("Successfully retrieved the sheet snapshot! [ENTER] to continue...")  # print success message
  input("")  # wait for user input to continue

  sheet_df = SPREADSHEET_OPS.create_df_from_snapshot(sheet_snapshot)

  # Extract team ID from the Team ID column
  team_id = SPREADSHEET_OPS.extract_team_id(sheet_df)  # extract team ID from sheet name
  print(f"Extracted Team ID: {team_id}")  # print the extracted team ID

  # update the DataFrame with hyperlinks
  # MATCHA, just add more fields, and add this to the original sheet_snapshot function (hyperlink support)
  sheet_snapshot_hyperlinks = SPREADSHEET_OPS.get_sheet_snapshot_with_rich_hyperlinks(TEAM_ID, "F2:G11")
  SPREADSHEET_OPS.print_sheet_snapshot(sheet_snapshot_hyperlinks)  # print the snapshot with hyperlinks    
  sheet_hyperlinks_df = SPREADSHEET_OPS.create_df_from_snapshot_hyperlinks(sheet_snapshot_hyperlinks)

  print("Updating DataFrame with hyperlinks...")
  SPREADSHEET_OPS.update_df(sheet_df, sheet_hyperlinks_df)
  # MATCHA: just auto apply the rich hyperlinks to sheet shapshots on first run, avoid all this extra work

  # store the DataFrame to CSV
  SPREADSHEET_OPS.store_sheet_df_to_csv(sheet_df, TEAM_ID)  # store updated DataFrame to CSV

  # store in JSON 

if __name__ == "__main__":
  main()