### Global Imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

### Local Imports
from __init__ import update_sys_path
update_sys_path()
from modules.api_clients.google_client.google_spreadsheet_api import establish_credentials, get_sheet_snapshot_basic, get_sheet_snapshot_with_hyperlinks, print_sheet_snapshot, create_df_from_snapshot, drop_sheet_df_columns, store_sheet_df_to_csv, extract_team_id

# (1) assign scopes (READ_SCOPE or WRITE_SCOPE)
# ... if change scope, delete config/token.json and re-run the script
# (2) set proper spreadsheet and sheet ID (SAMPLE_SPREADSHEET_ID, SAMPLE_SHEET_NAME, SAMPLE_SHEET_RANGE)

#########################
### TOKENS / SECURITY ###
#########################
# [token.json] stores the user's access and refresh tokens
# ... created automatically when authorization flow completes for the first time

##############
### SCOPES ###
##############
TOKEN_JSON_PATH = "config/token.json"
CREDENTIALS_JSON_PATH = "config/credentials.json"
SHEET_SNAPSHOT_DF_CSV_PATH = "data/processed/gcs_s2_roster_snapshot/"
READ_SCOPE = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
WRITE_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SCOPES = WRITE_SCOPE

##############################
### SPREADSHEET / SHEET ID ###
##############################
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1uvQafCH4xmiKDgW0lE84AvL1x5n385MU2bIYEaTTR1A"
# ... get this from the URL of the Google Sheet
SHEET_NAME = "[GCS-S2] Roster Information"
SHEET_RANGE = "B2:J"
# ... "A2:Z" will return all column data from A to Z, starting from row 2
# ... will not print if entire row is empty
SHEET_NAME_RANGE = f"{SHEET_NAME}!{SHEET_RANGE}" 

def main():
  creds = establish_credentials(SCOPES)  # establish client credentials 

  try:
    service = build("sheets", "v4", credentials=creds)
    sheet_snapshot = get_sheet_snapshot_basic(service, SPREADSHEET_ID, SHEET_NAME_RANGE)
    # print_sheet_snapshot(sheet_snapshot)
    sheet_df = create_df_from_snapshot(sheet_snapshot)
    sheet_df = drop_sheet_df_columns(sheet_df, ["RECENT CHAMPS"])  # drop unnecessary columns
    team_id = extract_team_id(sheet_df)  # extract team ID from sheet name
    print(f"Extracted Team ID: {team_id}")  # print the extracted team ID
    store_sheet_df_to_csv(sheet_df, SHEET_SNAPSHOT_DF_CSV_PATH + f"{team_id}.csv")  # store DataFrame to CSV
  except HttpError as err:
    print(err)

if __name__ == "__main__":
  main()