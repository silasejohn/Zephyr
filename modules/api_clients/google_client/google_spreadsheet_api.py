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
    
# given an updated section of a dataframe, update the original dataframe
def update_df(original_df, updated_df_section):
    # replace the columns of sheet_df with columns from sheet_hyperlinks_df if the column names match
    for col in updated_df_section.columns:
      if col in original_df.columns:
        original_df[col] = updated_df_section[col]  # replace the column in sheet_df with the one from sheet_hyperlinks_df
    
# *textformatruns* indicates a cell contains 2+ text parts with different formatting
# normalize_cell_parts() will combine these parts into a single part if there are no hyperlinks
def normalize_cell_parts(cell_parts):
    """Collapse text parts if there are no hyperlinks."""
    if all(part.get('hyperlink') is None for part in cell_parts):
        # No hyperlinks at all, so combine into one part
        return [{'text': ''.join(part['text'] for part in cell_parts), 'hyperlink': None}]
    else:
        return cell_parts
    
# applies normalize_cell_parts() to every cell in the sheet snapshot
def normalize_cell_parts_entire_sheet(sheet_snapshot):
    for row in sheet_snapshot:
      for i, cell_parts in enumerate(row):
          row[i] = normalize_cell_parts(cell_parts)
    return sheet_snapshot

def get_sheet_snapshot_with_rich_hyperlinks(service, spreadsheet_id, sheet_name_range):
    sheet = service.spreadsheets()
    result = sheet.get(
        spreadsheetId=spreadsheet_id,
        ranges=[sheet_name_range],
        includeGridData=True,
        fields='sheets.data.rowData.values(formattedValue,hyperlink,textFormatRuns)'
    ).execute()

    rows = result['sheets'][0]['data'][0]['rowData']
    snapshot = []

    for row in rows:
        snapshot_row = []
        for cell in row.get('values', []):
            cell_value = cell.get('formattedValue', '')
            rich_links = []
            runs = cell.get('textFormatRuns', []) # runs is a list of text format runs
            hyperlink = cell.get('hyperlink') # if the entire cell has a hyperlink

            if runs:
                # Parse multiple formatted spans
                for i, run in enumerate(runs):
                    start_index = run.get('startIndex', 0)
                    end_index = runs[i + 1]['startIndex'] if i + 1 < len(runs) else len(cell_value)
                    text_slice = cell_value[start_index:end_index]
                    uri = run.get('format', {}).get('link', {}).get('uri')
                    rich_links.append({'text': text_slice, 'hyperlink': uri})
                snapshot_row.append(rich_links)
            elif hyperlink:
                # Single full-cell hyperlink
                snapshot_row.append([{'text': cell_value, 'hyperlink': hyperlink}])
            else:
                # Plain cell with no hyperlink
                snapshot_row.append([{'text': cell_value, 'hyperlink': None}])
        snapshot.append(snapshot_row)

    if not snapshot:
        print("No data found in combined hyperlink snapshot")
        return None
    else:
        print("Combined hyperlink snapshot retrieved successfully")
        return snapshot

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

def create_df_from_snapshot_hyperlinks(sheet_snapshot):
    if not sheet_snapshot:
        print("Creating Empty DataFrame (no snapshot)...")
        return pd.DataFrame()

    print("Creating DataFrame from snapshot with hyperlinks...")

    # Extract column headers
    headers = [''.join(part['text'] for part in cell) for cell in sheet_snapshot[0]]

    data_rows = []
    for row in sheet_snapshot[1:]:
        formatted_row = []
        for cell in row:
            parts = []
            for part in cell:
                text = part['text'].replace('\n', '').strip()
                hyperlink = part['hyperlink'] if part['hyperlink'] else ""
                parts.append(f"{text}{{{hyperlink}}}")
            cell_str = '|'.join(parts)
            formatted_row.append(cell_str)
        data_rows.append(formatted_row)

    return pd.DataFrame(data_rows, columns=headers)

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


