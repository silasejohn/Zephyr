# from config.config import get_spreadsheet_config    
import sys        
import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN_JSON_PATH = "config/token.json"
CREDENTIALS_JSON_PATH = "config/credentials.json"
    
def establish_credentials(SCOPES):
    creds = None # start with no default credentials

    # if credentials exists, then store them
    if os.path.exists(TOKEN_JSON_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_JSON_PATH, SCOPES)

    # if there are no (valid) credentials, ask the user to log in / authorize
    if not creds or not creds.valid: 
        # if credentials are expired, then refresh them
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else: # if no credentials, then run the authorization flow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON_PATH, SCOPES)
            creds = flow.run_local_server(port=0) # run the local server to authorize the user

        # Save the credentials for the next run
        with open(TOKEN_JSON_PATH, "w") as token:
            token.write(creds.to_json())

    return creds

def get_sheet_snapshot_basic(service, spreadsheet_id, sheet_name_range):
    # call Google Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=spreadsheet_id, range=sheet_name_range)
        .execute()
    )
    sheet_snapshot = result.get("values", [])

    if not sheet_snapshot:
        print("No data found in sheet snapshot")
        return None
    else: 
        print("Sheet snapshot retrieved successfully")
        return sheet_snapshot

def get_sheet_snapshot_with_hyperlinks(service, spreadsheet_id, sheet_name_range):
    # call Google Sheets API
    sheet = service.spreadsheets()
    result_w_hyperlinks = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=sheet_name_range,
        fields='sheets.data.rowData.values.hyperlink,sheets.data.rowData.values.formattedValue'
    ).execute()
    sheet_snapshot = result_w_hyperlinks.get("values", [])

    if not sheet_snapshot:
        print("No data found in sheet snapshot")
        return None
    else: 
        print("Sheet snapshot retrieved successfully")
        return sheet_snapshot


def print_sheet_snapshot(sheet_snapshot):
    if not sheet_snapshot:
        return
    else:
       for sheet_row in sheet_snapshot:
            for cell in sheet_row:
                print(cell, end="\t")
            print()

def create_df_from_snapshot(sheet_snapshot):
    if not sheet_snapshot:
        print("Creating Empty DataFrame (no snapshot)...")
        return pd.DataFrame()  # return empty DataFrame if no data

    # Convert the sheet snapshot to a DataFrame
    df = pd.DataFrame(sheet_snapshot[1:], columns=sheet_snapshot[0])  # use first row as header

    # Replace Empty Strings (indicative of merged cells) with NaN, then forward fill merged values to these cells
    df.iloc[:, 0] = df.iloc[:, 0].replace('', pd.NA).ffill()

    # in every cell, replace "/n" with "|" to avoid issues with CSV formatting
    df = df.applymap(lambda x: x.replace('\n', '|') if isinstance(x, str) else x)

    return df

def drop_sheet_df_columns(sheet_df, columns_to_drop=None):
    
    if columns_to_drop is None: 
        return sheet_df # return if no columns to drop

    # drop specified columns and return the modified DataFrame
    sheet_df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
    return sheet_df

def store_sheet_df_to_csv(sheet_df, csv_file_path):
    if sheet_df.empty:
        print("DataFrame is empty. No CSV file created.")
        return

    try:
        sheet_df.to_csv(csv_file_path, index=False)
        print(f"DataFrame successfully stored to {csv_file_path}")
    except Exception as e:
        print(f"Error storing DataFrame to CSV: {e}")

def extract_team_id(sheet_df):
    if sheet_df.empty:
        return None
    return sheet_df.iloc[0, 0]  # return the first cell value as team ID