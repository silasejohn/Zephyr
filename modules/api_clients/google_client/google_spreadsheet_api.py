# from config.config import get_spreadsheet_config    
import sys        
import os.path
import pandas as pd
import string

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


### Local Imports
from __init__ import update_sys_path
update_sys_path()
from modules.utils.color_utils import warning_print, error_print, info_print, success_print

READ_SCOPE = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
WRITE_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]


#############################
### CLASS SPREADSHEET_OPS ###
#############################
class SPREADSHEET_OPS:
    TOKEN_JSON_PATH = "config/token.json"
    CREDENTIALS_JSON_PATH = "config/credentials.json"
    SHEET_SNAPSHOT_DF_CSV_PATH = "data/processed/gcs_s2_roster_snapshot/"
    SERVICE = None
    SPREADSHEET_ID = None

    ### STATIC INFO per Sheet in Spreadsheet
    SHEET_INFO = {} 
    # [Field 1] NAME (string): The name of the sheet.
    # [Field 2] OPERATING_RANGE (string): The range of the sheet, e.g., "A1:Z100".

    #########################
    ### GETTERS / SETTERS ###
    #########################

    @staticmethod
    def set_spreadsheet_id(spreadsheet_id):
        """
        Set the spreadsheet ID for the Google Sheets API operations.
        [param] spreadsheet_id: The ID of the Google Spreadsheet.
        """
        SPREADSHEET_OPS.SPREADSHEET_ID = spreadsheet_id
        info_print(f"Spreadsheet ID set to: {SPREADSHEET_OPS.SPREADSHEET_ID}")

    @staticmethod
    def set_service(service):
        """
        Set the Google Sheets API service for the operations.
        [param] service: The Google Sheets API service object.
        """
        SPREADSHEET_OPS.SERVICE = service
        info_print("Google Sheets API service set.")
    
    @staticmethod
    def get_service():
        """
        Get the Google Sheets API service.
        [return] service: The Google Sheets API service object.
        """
        if SPREADSHEET_OPS.SERVICE is None:
            error_print("Google Sheets API service is not set. Please call set_service() first.")
            sys.exit(1)
        return SPREADSHEET_OPS.SERVICE
    
    @staticmethod
    def get_spreadsheet_id():
        """
        Get the Google Spreadsheet ID.
        [return] spreadsheet_id: The ID of the Google Spreadsheet.
        """
        if SPREADSHEET_OPS.SPREADSHEET_ID is None:
            error_print("Spreadsheet ID is not set. Please call set_spreadsheet_id() first.")
            sys.exit(1)
        return SPREADSHEET_OPS.SPREADSHEET_ID
    
    @staticmethod
    def get_spreadsheet_sheet_titles():
        """
        Get the titles of all sheets in the Google Spreadsheet.
        [return] sheet_titles: List of sheet titles in the spreadsheet.
        """
        if not SPREADSHEET_OPS.SHEET_TITLES:
            error_print("Sheet titles are not initialized. Please call initialize() first.")
            sys.exit(1)
        return SPREADSHEET_OPS.SHEET_TITLES
    
    ##################################################
    ###  STATIC METHODS FOR SPREADSHEET OPERATIONS ###
    ##################################################
    
    @staticmethod
    def initialize(scopes, spreadsheet_id):
        if scopes == "READ": 
            scopes = READ_SCOPE
        elif scopes == "WRITE":
            scopes = WRITE_SCOPE
        else:
            warning_print("Defaulting to READ_SCOPE. Remember to delete config/token.json if you change scopes.")
            scopes = READ_SCOPE  # default to read scope if not specified
            input("Press [ENTER] to continue...")  # wait for user input to continue

        try: # establish client credentials, sheets service, initialize the spreadsheet operations class
            # establish client credentials 
            creds = SPREADSHEET_OPS.establish_credentials(scopes)
            sheets_svc = build("sheets", "v4", credentials=creds)
            SPREADSHEET_OPS.set_service(sheets_svc)  # set the service for the spreadsheet operations
            SPREADSHEET_OPS.set_spreadsheet_id(spreadsheet_id)
            SPREADSHEET_OPS.initialize_sheet_titles()  # initialize the Google Spreadsheet API operations
            SPREADSHEET_OPS.initialize_sheet_data_ranges()  # initialize the data ranges for the sheets

            print("\n")
            SPREADSHEET_OPS.print_sheet_info_dictionary()  # print the sheet info dictionary
            success_print("SPREADSHEET_OPS class initialized successfully. [ENTER] to continue...")
            input("") 
        except HttpError as err:
            print(err)

    @staticmethod
    def update_spreadsheet_static_info():
        """
        Update the static information for the Google Spreadsheet operations.
        This includes setting the spreadsheet ID and initializing the sheet titles.
        """
        # update sheet names and IDs
        SPREADSHEET_OPS.initialize_sheet_titles()  # initialize the sheet titles
        SPREADSHEET_OPS.initialize_sheet_data_ranges()  # initialize the data ranges for the sheets
        SPREADSHEET_OPS.print_sheet_info_dictionary()  # print the sheet info dictionary
        success_print("Spreadsheet static information updated successfully.")

    @staticmethod
    def initialize_sheet_titles():
        sheet_titles = SPREADSHEET_OPS.get_sheet_names()
        print(f"Initialized sheet titles: {sheet_titles}")  # print the initialized sheet title

        sheet_team_ids = [title.split("]")[0].split("[")[1] for title in sheet_titles] # splice out team IDs from sheet titles

        # set up a dict to track info per each sheet
        SPREADSHEET_OPS.SHEET_INFO = {
            team_id: {
                "NAME": title,
                "READY?": False,
                "OPERATING_RANGE": ""
            }
            for team_id, title in zip(sheet_team_ids, sheet_titles)
        }

        print("\n")

    @staticmethod
    def establish_credentials(SCOPES):
        """
        Establishes credentials for Google Sheets API.
        [param] SCOPES: List of scopes for the API access.
        [return] creds: Credentials object for the authenticated user.
        """
        creds = None # start with no default credentials

        # if credentials exists, then store them
        if os.path.exists(SPREADSHEET_OPS.TOKEN_JSON_PATH):
            creds = Credentials.from_authorized_user_file(SPREADSHEET_OPS.TOKEN_JSON_PATH, SCOPES)

        # if there are no (valid) credentials, ask the user to log in / authorize
        if not creds or not creds.valid: 
            # if credentials are expired, then refresh them
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else: # if no credentials, then run the authorization flow
                flow = InstalledAppFlow.from_client_secrets_file(SPREADSHEET_OPS.CREDENTIALS_JSON_PATH, SCOPES)
                creds = flow.run_local_server(port=0) # run the local server to authorize the user

            # Save the credentials for the next run
            with open(SPREADSHEET_OPS.TOKEN_JSON_PATH, "w") as token:
                token.write(creds.to_json())

        return creds

    @staticmethod
    def get_sheet_data_range(sheet_name):
        """
        Get the data range of a specific sheet in the Google Spreadsheet.
        [param] sheet_name: The name of the sheet to get the data range for.
        [return] data_range: The A1 notation of the data range in the sheet.
        - default is "A1" if the sheet is empty.
        """
        try: # get all possible values in the sheet
            result = SPREADSHEET_OPS.SERVICE.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
                range=sheet_name
            ).execute()

            response = result.get('values', [])

            if not response:
                warning_print(f"Sheet '{sheet_name}' is empty or does not exist. Returning default range 'A1'.")
                return f"{sheet_name}!A1"  # Empty sheet fallback

            max_row = len(response)
            max_col = max(len(row) for row in response if row)  # Handle jagged rows

            end_col_letter = SPREADSHEET_OPS.col_num_to_letter(max_col)
            sheet_operating_range = f"{sheet_name}!A1:{end_col_letter}{max_row}"
            
            # add to corresponding (same idx) in 
            return sheet_operating_range

        except HttpError as err:
            print(f"An error occurred: {err}")
            return None
    
    @staticmethod
    def initialize_sheet_data_ranges():
        """
        Initialize the data ranges for all sheets in the Google Spreadsheet.
        This will update the SHEET_INFO dictionary with the operating range for each sheet.
        """
        if not SPREADSHEET_OPS.SHEET_INFO:
            error_print("Sheet titles are not initialized. Please call initialize_sheet_titles() first.")
            sys.exit(1)

        for team_id, info in SPREADSHEET_OPS.SHEET_INFO.items():
            sheet_name = info["NAME"]
            operating_range = SPREADSHEET_OPS.get_sheet_data_range(sheet_name)

            if operating_range:
                info["OPERATING_RANGE"] = operating_range
                info["READY?"] = True
            else:
                error_print(f"Failed to get operating range for sheet '{sheet_name}'.")
                info["READY?"] = False
        
    @staticmethod
    def get_sheet_snapshot_basic(team_id, range_limiter=None):
        """
        Retrieve a basic snapshot of a Google Sheet.
        [param] service: Google Sheets API service object.
        [param] spreadsheet_id: ID of the Google Sheet.
        [param] team_id: The ID of the team to get the sheet snapshot for.
        [return] sheet_snapshot: List of lists representing the sheet data.
        """

        if range_limiter is None:
            # get the sheet name and range for the team ID
            if team_id not in SPREADSHEET_OPS.SHEET_INFO:
                error_print(f"Team ID '{team_id}' does not exist in the sheet info dictionary.")
                return None
            sheet_name_range = SPREADSHEET_OPS.SHEET_INFO[team_id]["OPERATING_RANGE"]
        else: 
            # use the provided range_limiter to get the sheet name and range
            sheet_name_range = f"{SPREADSHEET_OPS.SHEET_INFO[team_id]['NAME']}!{range_limiter}"
            
        info_print(f"Retrieving sheet snapshot for team ID '{team_id}' with range '{sheet_name_range}'...")

        sheet = SPREADSHEET_OPS.SERVICE.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID, range=sheet_name_range)
            .execute()
        )
        sheet_snapshot = result.get("values", [])

        if not sheet_snapshot:
            print("No data found in sheet snapshot")
            return None
        else: 
            print("Sheet snapshot retrieved successfully")
            return sheet_snapshot
    
    @staticmethod
    def update_df(original_df, updated_df_section):
        """
        Update the original DataFrame with the updated section DataFrame.
        [param] original_df: The original DataFrame to be updated.
        [param] updated_df_section: The DataFrame section with updated data.
        [return] None: The original DataFrame is modified in place.
        """
        # replace the columns of sheet_df with columns from sheet_hyperlinks_df if the column names match
        for col in updated_df_section.columns:
            if col in original_df.columns:
                original_df[col] = updated_df_section[col]  # replace the column in sheet_df with the one from sheet_hyperlinks_df
        
    @staticmethod
    def normalize_cell_parts(cell_parts):
        """
        Normalize cell parts by combining text parts (textformatruns) without hyperlinks into a single part.
        [param] cell_parts: List of dictionaries representing cell parts with text and hyperlinks.
        """
        if all(part.get('hyperlink') is None for part in cell_parts):
            # No hyperlinks at all, so combine into one part
            return [{'text': ''.join(part['text'] for part in cell_parts), 'hyperlink': None}]
        else:
            return cell_parts

    @staticmethod   
    def normalize_cell_parts_entire_sheet(sheet_snapshot):
        """
        Normalize all cell parts in the sheet snapshot.
        [param] sheet_snapshot: List of lists representing the sheet data.
        [return] sheet_snapshot: The modified sheet snapshot with normalized cell parts.
        """
        for row in sheet_snapshot:
            for i, cell_parts in enumerate(row):
                row[i] = SPREADSHEET_OPS.normalize_cell_parts(cell_parts)
        return sheet_snapshot

    @staticmethod
    def get_sheet_snapshot_with_rich_hyperlinks(team_id, range_limiter=None):
        """
        Retrieve a snapshot of a Google Sheet with rich hyperlinks.
        [param] service: Google Sheets API service object.
        [param] spreadsheet_id: ID of the Google Sheet.
        [param] sheet_name_range: Range of the sheet to retrieve (e.g., "Sheet1!A1:C10").
        [return] snapshot: List of lists representing the sheet data with hyperlinks.
        """

        if range_limiter is None:
            # get the sheet name and range for the team ID
            if team_id not in SPREADSHEET_OPS.SHEET_INFO:
                error_print(f"Team ID '{team_id}' does not exist in the sheet info dictionary.")
                return None
            sheet_name_range = SPREADSHEET_OPS.SHEET_INFO[team_id]["OPERATING_RANGE"]
        else: 
            # use the provided range_limiter to get the sheet name and range
            sheet_name_range = f"{SPREADSHEET_OPS.SHEET_INFO[team_id]['NAME']}!{range_limiter}"
            
        info_print(f"Retrieving sheet snapshot for team ID '{team_id}' with range '{sheet_name_range}'...")

        sheet = SPREADSHEET_OPS.SERVICE.spreadsheets()
        result = sheet.get(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            ranges=[sheet_name_range],
            includeGridData=True,
            fields='sheets.data.rowData.values(formattedValue,hyperlink,textFormatRuns)'
        ).execute()
        
        rows = result['sheets'][0]['data'][0]['rowData']
        snapshot = []

        # iterate through each row and extract cell values and hyperlinks
        for row in rows:
            snapshot_row = []
            for cell in row.get('values', []):
                cell_value = cell.get('formattedValue', '')
                rich_links = []
                runs = cell.get('textFormatRuns', []) # runs is a list of text format runs
                hyperlink = cell.get('hyperlink') # if the entire cell has a hyperlink

                if runs:
                    # parse multiple formatted spans
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
            snapshot = SPREADSHEET_OPS.normalize_cell_parts_entire_sheet(snapshot)  # normalize the cell parts in the snapshot
            print("Combined hyperlink snapshot retrieved successfully")
            return snapshot

    @staticmethod
    def print_sheet_snapshot(sheet_snapshot):
        """
        Print the sheet snapshot in a tabular format.
        [param] sheet_snapshot: List of lists representing the sheet data."""
        if not sheet_snapshot:
            return
        else:
            for sheet_row in sheet_snapshot:
                    for cell in sheet_row:
                        print(cell, end="\t")
                    print()

    @staticmethod
    def print_sheet_info_dictionary():
        info_print("\n***[SHEET INFO DICTIONARY]***")
        for sheet_name, info in SPREADSHEET_OPS.SHEET_INFO.items():
            print(f"Sheet Name: {sheet_name}, Info: {info}")

    @staticmethod
    def create_df_from_snapshot(sheet_snapshot):
        """
        Create a DataFrame from a sheet snapshot.
        [param] sheet_snapshot: List of lists representing the sheet data.
        [return] df: DataFrame created from the sheet snapshot."""
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

    @staticmethod
    def create_df_from_snapshot_hyperlinks(sheet_snapshot):
        """
        Create a DataFrame from a sheet snapshot with hyperlinks.
        [param] sheet_snapshot: List of lists representing the sheet data with hyperlinks.
        [return] df: DataFrame created from the sheet snapshot with hyperlinks.
        """
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

    @staticmethod
    def drop_sheet_df_columns(sheet_df, columns_to_drop=None):
        """        
        Drop specified columns from a DataFrame.
        [param] sheet_df: DataFrame from which to drop columns.
        [param] columns_to_drop: List of column names to drop. If None, no columns are dropped.
        [return] sheet_df: Modified DataFrame with specified columns dropped."""
        if columns_to_drop is None: 
            return sheet_df # return if no columns to drop

        # drop specified columns and return the modified DataFrame
        sheet_df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
        return sheet_df

    @staticmethod
    def store_sheet_df_to_csv(sheet_df, team_id):
        """
        Store a DataFrame to a CSV file.
        [param] sheet_df: DataFrame to be stored.
        [param] csv_file_path: Path where the CSV file will be saved.
        [return] None: The DataFrame is stored in the specified CSV file.
        """
        if sheet_df.empty:
            print("DataFrame is empty. No CSV file created.")
            return

        try:
            csv_file_path = SPREADSHEET_OPS.SHEET_SNAPSHOT_DF_CSV_PATH + f"{team_id}.csv"
            sheet_df.to_csv(csv_file_path, index=False)
            print(f"DataFrame successfully stored to {csv_file_path}")
        except Exception as e:
            print(f"Error storing DataFrame to CSV: {e}")

    @staticmethod
    def extract_team_id(sheet_df):
        """
        Extract the team ID from the first cell of the DataFrame.
        [param] sheet_df: DataFrame containing the sheet data.
        [return] team_id: The team ID extracted from the first cell, or None if the DataFrame is empty.
        """
        if sheet_df.empty:
            return None
        return sheet_df.iloc[0, 0]  # return the first cell value as team ID

    @staticmethod
    def edit_cell(sheet_name, cell_id, cell_value):
        """
        Edit a specific cell in a Google Sheet.
        [param] service: Google Sheets API service object.
        [param] spreadsheet_id: ID of the Google Sheet.
        [param] sheet_name: Name of the sheet where the cell is located.
        [param] cell_id: ID of the cell to edit (e.g., "C1").
        [param] cell_value: New value to set in the specified cell.
        [return] None: The specified cell is updated with the new value.
        """
        SHEET_NAME_CELL = f"{sheet_name}!{cell_id}" # create the full range for the cell to edit
        payload = { 'values': [[cell_value]] }
        try:
            SPREADSHEET_OPS.SERVICE.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID, 
                range=SHEET_NAME_CELL, 
                valueInputOption='RAW',
                body=payload
            ).execute()
            success_print(f"Cell {cell_id} in {sheet_name} updated to '{cell_value}'")
        except HttpError as err:
            print(f"An error occurred: {err}")

    @staticmethod
    def create_sheet_for_team(team_id, team_name):
        """
        Create a new sheet in a Google Spreadsheet for a specific team.
        [param] team_id: ID of the team for which the sheet is being created.
        [param] team_name: Name of the team for which the sheet is being created.
        [return] NEW_SHEET_NAME: The name of the newly created sheet, or None if an error occurs.
        """

        NEW_SHEET_NAME = f"[{team_id}] {team_name}"  # format the new sheet name

        # check if the sheet already exists
        status = SPREADSHEET_OPS.check_sheet_exists(NEW_SHEET_NAME)
        if status:
            warning_print(f"Sheet '{NEW_SHEET_NAME}' already exists. No new sheet created.")
            return NEW_SHEET_NAME
        warning_print(f"Creating new sheet for team '{team_name}' with ID '{team_id}'...")
        
        payload = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': NEW_SHEET_NAME
                        }
                    }
                }
            ]
        }

        try:
            response = SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
                body=payload
            ).execute()
            
            success_print(f"Sheet '{NEW_SHEET_NAME}' created successfully.")

            # Add Header Row 
            SPREADSHEET_OPS.create_GCS_scout_sheet_roster_section_header_row(NEW_SHEET_NAME, "B4")

            # update the SHEET_INFO dictionary with the new sheet info
            SPREADSHEET_OPS.update_spreadsheet_static_info()  # update the static info after creating the new sheet
        
            # return response
            # return new sheet name 
            return NEW_SHEET_NAME
        except HttpError as err:
            print(f"An error occurred: {err}")
            return None

    @staticmethod
    def check_sheet_exists(sheet_name):
        """
        Check if a sheet with the given name exists in the Google Spreadsheet.
        [param] service: Google Sheets API service object.
        [param] spreadsheet_id: ID of the Google Spreadsheet.
        [param] sheet_name: Name of the sheet to check for existence.
        [return] exists: True if the sheet exists, False otherwise.
        """
        try:
            spreadsheet = SPREADSHEET_OPS.SERVICE.spreadsheets().get(spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID).execute()
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            return sheet_name in sheet_names
        except HttpError as err:
            print(f"An error occurred: {err}")
            return False

    @staticmethod
    def get_sheet_names():
        """
        Retrieve the names of all sheets in a Google Spreadsheet.
        [param] service: Google Sheets API service object.
        [param] spreadsheet_id: ID of the Google Spreadsheet.
        [return] sheet_names: List of names of all sheets in the spreadsheet, or an empty list if an error occurs.
        """
        try:
            spreadsheet = SPREADSHEET_OPS.SERVICE.spreadsheets().get(spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID).execute()
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            return sheet_names
        except HttpError as err:
            print(f"An error occurred: {err}")
            return []
    
    @staticmethod
    def create_GCS_scout_sheet_roster_section_header_row(sheet_name, cell_id):
        """
        Create a header row for the team roster section in a Google Sheet.
        [param] cell_id: ID of the cell where the header row will be created (e.g., "A1").
        [return] None: The header row is created in the specified cell.
        """
        header_values = [["Discord Username", "Rank Score", "Role Priority", "Profile (OP.GG)", "Profile (LOG)", "Current Rank", "Peak Rank"]]
        range_ = f"{sheet_name}!{cell_id}"
        body = {'values': header_values}

        try:
            SPREADSHEET_OPS.SERVICE.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
                range=range_,
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f"Roster header row written to {range_}")
        except HttpError as err:
            print(f"An error occurred while writing header row: {err}")

    @staticmethod
    def delete_sheet(sheet_name):
        """
        Delete a sheet from the Google Spreadsheet.
        [param] sheet_name: Name of the sheet to be deleted.
        [return] None: The specified sheet is deleted from the spreadsheet.
        """
        try:
            # Get the sheet ID for the specified sheet name
            spreadsheet = SPREADSHEET_OPS.SERVICE.spreadsheets().get(spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID).execute()
            sheets = spreadsheet.get('sheets', [])
            sheet_id = next((sheet['properties']['sheetId'] for sheet in sheets if sheet['properties']['title'] == sheet_name), None)

            if not sheet_id:
                warning_print(f"Sheet '{sheet_name}' does not exist. No deletion performed.")
                return

            # Prepare the request to delete the sheet
            requests = [{
                'deleteSheet': {
                    'sheetId': sheet_id
                }
            }]

            body = {'requests': requests}
            SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
                body=body
            ).execute()

            success_print(f"Sheet '{sheet_name}' deleted successfully.")
        except HttpError as err:
            print(f"An error occurred while deleting the sheet: {err}")
    #########################
    ### UTILITY FUNCTIONS ### 
    #########################
    @staticmethod
    def col_num_to_letter(n):
        """
        Convert a column number to an Excel-style column letter.
        [param] n: The column number (1-based index).
        [return] result: The corresponding column letter(s) in A1 notation.
        """
        result = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            result = chr(65 + remainder) + result
        return result





