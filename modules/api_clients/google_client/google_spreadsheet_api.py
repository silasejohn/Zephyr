# from config.config import get_spreadsheet_config    
import sys        
import os.path
import pandas as pd
import string, json
import re               # used in A1 to Grid Coordinate Conversion

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
    def create_sheet_for_team(team_id, team_name, mode="normal"):
        """
        Create a new sheet in a Google Spreadsheet for a specific team.
        [param] team_id: ID of the team for which the sheet is being created.
        [param] team_name: Name of the team for which the sheet is being created.
        [return] NEW_SHEET_NAME: The name of the newly created sheet, or None if an error occurs.
        """

        if mode == "reset":
            # delete the existing sheet for the team if it exists
            existing_sheet_name = f"[{team_id}] {team_name}"
            if SPREADSHEET_OPS.check_sheet_exists(existing_sheet_name):
                SPREADSHEET_OPS.delete_sheet(existing_sheet_name)
                warning_print(f"Deleted existing sheet '{existing_sheet_name}' before creating a new one.")

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

            # Add Data for Each Column

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
        header_values = [["Discord Username", "Rank Score", "Role Priority", "Profile (OP.GG)", "Profile (LOG)", "Current Rank", "Peak Rank", "Recent Champs Played"]]
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
    def insert_player_data(team_id, header_row_num, payload, start_col_letter="A"):
        """
        Inserts a new row of player data under the first empty row below the header row.
        :param team_id: Key to look up the sheet name.
        :param header_row_num: String number of the row containing headers (e.g., "4").
        :param payload: List of values to insert (length must match number of headers).
        :param start_col_letter: Letter of the first column containing a header (e.g., "B").
        """

        # Get sheet name from team ID
        if team_id not in SPREADSHEET_OPS.SHEET_INFO:
            raise ValueError(f"Team ID '{team_id}' does not exist in the spreadsheet.")
        sheet_name = SPREADSHEET_OPS.SHEET_INFO[team_id]["NAME"]

        # Compute header range (assume max header width 26 for now)
        header_range = f"{sheet_name}!{start_col_letter}{header_row_num}:Z{header_row_num}"
        result = SPREADSHEET_OPS.SERVICE.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            range=header_range
        ).execute()
        headers = result.get('values', [[]])[0]
        num_headers = len(headers)

        # Error Checks if no headers found or payload length mismatch
        if num_headers == 0:
            raise ValueError(f"No headers found in row {header_row_num} starting from column {start_col_letter}.")

        if len(payload) != num_headers:
            raise ValueError(f"Expected {num_headers} values (based on headers) but got {len(payload)} values in payload.")

        # Compute row offset for insertion (do not overwrite existing player row data / info)
        row_offset = int(header_row_num) + 1

        # Check for next available row in first header column (e.g., column B)
        first_data_col_range = f"{sheet_name}!{start_col_letter}{row_offset}:{start_col_letter}"
        data = SPREADSHEET_OPS.SERVICE.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            range=first_data_col_range
        ).execute()
        existing_rows = data.get("values", [])
        next_row_number = row_offset + len(existing_rows)

        # Compute the target range for insertion
        # col_start = start_col_letter.upper()
        start_col_index = ord(start_col_letter.upper()) - ord('A')
        # col_end = SPREADSHEET_OPS.col_letter_offset(col_start, num_headers - 1)
        # target_range = f"{sheet_name}!{col_start}{next_row_number}:{col_end}{next_row_number}"

        # Build CellData objects (rich text formatting if needed)
        row_cells = []
        for value in payload:
            if isinstance(value, str) and "{" in value:
                row_cells.append(SPREADSHEET_OPS.build_rich_text_cell(value))
            else:
                row_cells.append({
                    "userEnteredValue": {"stringValue": value}
                })

        # Prepare batchUpdate request
        requests = [{
            "updateCells": {
                "rows": [{"values": row_cells}],
                "fields": "*",
                "start": {
                    "sheetId": SPREADSHEET_OPS.get_sheet_id_by_name(sheet_name),
                    "rowIndex": next_row_number - 1,
                    "columnIndex": start_col_index
                }
            }
        }]

        # Execute the batchUpdate request
        SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            body={"requests": requests}
        ).execute()

        print(f"Inserted rich-text row at {sheet_name}!Row {next_row_number}")
            
        # body = { "values": [payload] }
        # # Update the sheet
        # SPREADSHEET_OPS.SERVICE.spreadsheets().values().update(
        #     spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
        #     range=target_range,
        #     valueInputOption='RAW',
        #     body=body
        # ).execute()
        # print(f"Inserted row at {target_range}")
        
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
    
    @staticmethod
    def get_sheet_id_by_name(target_sheet_name):
        """
        Get the sheet ID for a given sheet name in a Google Spreadsheet.
        :param service: Google Sheets API service object.
        :paramspreadsheet_id: ID of the Google Spreadsheet.
        :param target_sheet_name: Name of the sheet to find.
        :return: The sheet ID if found, otherwise raises ValueError.
        """
        response = SPREADSHEET_OPS.SERVICE.spreadsheets().get(spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID).execute()
        sheets = response.get("sheets", [])
        
        for sheet in sheets:
            title = sheet.get("properties", {}).get("title")
            if title == target_sheet_name:
                return sheet.get("properties", {}).get("sheetId")
        
        raise ValueError(f"Sheet name '{target_sheet_name}' not found in spreadsheet.")

    @staticmethod
    def build_rich_text_cell(text_with_links):
        """
        Build a rich text cell for Google Sheets given cell content with embedded links
        :param text_with_links: String containing text and links in the format "text{url}|text{url}".
        :return: Dictionary representing the rich text cell with text and link formatting.
        """
        # count the number of "{" in the string to determine if there are links. if there are 2+ print "HIIII"
        parts = []
        # if text_with_links.count("{") >= 2:
        parts = text_with_links.split("|")
        # elif text_with_links.count("{") >= 1:
            # parts = [text_with_links]  
        # else:   
        #     parts = [text_with_links]
        
        full_text = ""
        text_format_runs = []
        current_index = 0

        for part in parts:
            if "{" in part and "}" in part:
                text, link = part.split("{", 1)
                link = link.rstrip("}")
            else:
                text = part
                link = None

            text = text.strip() + "\n"
            full_text += text

            run = {
                "startIndex": current_index,
                "format": {
                    "link": {"uri": link} if link else {}
                }
            }
            text_format_runs.append(run)
            current_index += len(text)

        return {
            "userEnteredValue": {"stringValue": full_text.rstrip()},
            "textFormatRuns": text_format_runs
        }
    
    #########################
    ### STYLING FUNCTIONS ### 
    #########################
    @staticmethod
    def apply_text_style(team_id, start_a1, end_a1, style_dict):
        """
        Applies text style to a specified cell range.
        :param sheet_id: Integer sheet ID (not sheet name!)
        :param start_a1: Start of the A1 range (e.g. "B4")
        :param end_a1: End of the A1 range (e.g. "H20")
        :param style_dict: Dict of text style properties (e.g. {"bold": True})
        """
        # given team_id, get the sheet name then sheet id
        if team_id not in SPREADSHEET_OPS.SHEET_INFO:
            error_print(f"Team ID '{team_id}' does not exist in the spreadsheet.")
            return
        sheet_name = SPREADSHEET_OPS.SHEET_INFO[team_id]["NAME"]
        sheet_id = SPREADSHEET_OPS.get_sheet_id_by_name(sheet_name)

        start_col, start_row = SPREADSHEET_OPS.a1_to_grid_coords(start_a1)
        end_col, end_row = SPREADSHEET_OPS.a1_to_grid_coords(end_a1)

        # Google Sheets ranges are exclusive at the end, so add +1
        end_col += 1
        end_row += 1

        request_body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": style_dict
                            }
                        },
                        "fields": "userEnteredFormat.textFormat"
                    }
                }
            ]
        }

        SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            body=request_body
        ).execute()

    @staticmethod
    def make_range_bold(team_id, start_a1, end_a1):
        SPREADSHEET_OPS.apply_text_style(team_id, start_a1, end_a1, {"bold": True})

    @staticmethod
    def make_range_underline(team_id, start_a1, end_a1):
        SPREADSHEET_OPS.apply_text_style(team_id, start_a1, end_a1, {"underline": True})

    @staticmethod
    def make_range_italic(team_id, start_a1, end_a1):
        SPREADSHEET_OPS.apply_text_style(team_id, start_a1, end_a1, {"italic": True})

    @staticmethod
    def make_range_strikethrough(team_id, start_a1, end_a1):
        SPREADSHEET_OPS.apply_text_style(team_id, start_a1, end_a1, {"strikethrough": True})

    @staticmethod
    def make_range_bold_italic(team_id, start_a1, end_a1):
        SPREADSHEET_OPS.apply_text_style(team_id, start_a1, end_a1, {"bold": True, "italic": True})

    @staticmethod
    def make_range_bold_underline(team_id, start_a1, end_a1):
        SPREADSHEET_OPS.apply_text_style(team_id, start_a1, end_a1, {"bold": True, "underline": True})

    @staticmethod
    def apply_cell_background_color(team_id, start_a1, end_a1, rgb_color):

        # given team_id, get the sheet name then sheet id
        if team_id not in SPREADSHEET_OPS.SHEET_INFO:
            error_print(f"Team ID '{team_id}' does not exist in the spreadsheet.")
            return
        sheet_name = SPREADSHEET_OPS.SHEET_INFO[team_id]["NAME"]
        sheet_id = SPREADSHEET_OPS.get_sheet_id_by_name(sheet_name)

        start_col, start_row = SPREADSHEET_OPS.a1_to_grid_coords(start_a1)
        end_col, end_row = SPREADSHEET_OPS.a1_to_grid_coords(end_a1)
        end_col += 1
        end_row += 1

        request_body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": rgb_color[0] / 255.0,
                                    "green": rgb_color[1] / 255.0,
                                    "blue": rgb_color[2] / 255.0
                                }
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                }
            ]
        }

        SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            body=request_body
        ).execute()

    @staticmethod
    def apply_horizontal_alignment(team_id, start_a1, end_a1, alignment="CENTER"):
        """
        Applies horizontal alignment to a specified cell range.
        :param alignment: One of 'LEFT', 'CENTER', 'RIGHT'
        """
        if team_id not in SPREADSHEET_OPS.SHEET_INFO:
            error_print(f"Team ID '{team_id}' does not exist in the spreadsheet.")
            return
        sheet_name = SPREADSHEET_OPS.SHEET_INFO[team_id]["NAME"]
        sheet_id = SPREADSHEET_OPS.get_sheet_id_by_name(sheet_name)

        start_col, start_row = SPREADSHEET_OPS.a1_to_grid_coords(start_a1)
        end_col, end_row = SPREADSHEET_OPS.a1_to_grid_coords(end_a1)
        end_col += 1
        end_row += 1

        request_body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "horizontalAlignment": alignment
                            }
                        },
                        "fields": "userEnteredFormat.horizontalAlignment"
                    }
                }
            ]
        }

        SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            body=request_body
        ).execute()

    @staticmethod
    def apply_vertical_alignment(team_id, start_a1, end_a1, alignment="MIDDLE"):
        """
        Applies vertical alignment to a specified cell range.
        :param alignment: One of 'TOP', 'MIDDLE', 'BOTTOM'
        """
        if team_id not in SPREADSHEET_OPS.SHEET_INFO:
            error_print(f"Team ID '{team_id}' does not exist in the spreadsheet.")
            return
        sheet_name = SPREADSHEET_OPS.SHEET_INFO[team_id]["NAME"]
        sheet_id = SPREADSHEET_OPS.get_sheet_id_by_name(sheet_name)

        start_col, start_row = SPREADSHEET_OPS.a1_to_grid_coords(start_a1)
        end_col, end_row = SPREADSHEET_OPS.a1_to_grid_coords(end_a1)
        end_col += 1
        end_row += 1

        request_body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "verticalAlignment": alignment
                            }
                        },
                        "fields": "userEnteredFormat.verticalAlignment"
                    }
                }
            ]
        }

        SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            body=request_body
        ).execute()

    @staticmethod
    def auto_resize_columns_to_fit_text(team_id, start_a1, end_a1, extra_pixels=20):
        """
        Automatically resizes columns in the given range to fit the text.
        :param team_id: Identifier used to get sheet name/id
        :param start_a1: Start cell in A1 notation (e.g., "B4")
        :param end_a1: End cell in A1 notation (e.g., "F20")
        """
        if team_id not in SPREADSHEET_OPS.SHEET_INFO:
            error_print(f"Team ID '{team_id}' does not exist in the spreadsheet.")
            return

        sheet_name = SPREADSHEET_OPS.SHEET_INFO[team_id]["NAME"]
        sheet_id = SPREADSHEET_OPS.get_sheet_id_by_name(sheet_name)

        start_col, _ = SPREADSHEET_OPS.a1_to_grid_coords(start_a1)
        end_col, _ = SPREADSHEET_OPS.a1_to_grid_coords(end_a1)
        end_col += 1  # Google Sheets API is exclusive on the upper bound

        request_body = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": start_col,
                            "endIndex": end_col
                        }
                    }
                }
            ]
        }

        SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            body=request_body
        ).execute()

        SPREADSHEET_OPS.expand_column_widths(team_id, start_a1, end_a1, extra_pixels=20)

    @staticmethod
    def expand_column_widths(team_id, start_a1, end_a1, extra_pixels=20):
        """
        Adds a fixed number of pixels to the current width of each column in the range.
        :param team_id: ID of the team to locate the correct sheet
        :param start_a1: Start of the A1 range (e.g. "B4")
        :param end_a1: End of the A1 range (e.g. "F20")
        :param extra_pixels: Number of pixels to add to each column (default: 20)
        """
        # Resolve sheet ID
        if team_id not in SPREADSHEET_OPS.SHEET_INFO:
            error_print(f"Team ID '{team_id}' does not exist in the spreadsheet.")
            return
        sheet_name = SPREADSHEET_OPS.SHEET_INFO[team_id]["NAME"]
        sheet_id = SPREADSHEET_OPS.get_sheet_id_by_name(sheet_name)

        # Convert A1 to grid coordinates
        start_col, _ = SPREADSHEET_OPS.a1_to_grid_coords(start_a1)
        end_col, _ = SPREADSHEET_OPS.a1_to_grid_coords(end_a1)
        end_col += 1

        # Get current spreadsheet metadata for column sizes
        metadata = SPREADSHEET_OPS.SERVICE.spreadsheets().get(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            ranges=[f"'{sheet_name}'"],
            fields="sheets.data.columnMetadata"
        ).execute()

        column_metadata = metadata["sheets"][0]["data"][0].get("columnMetadata", [])

        requests = []
        for col in range(start_col, end_col):
            try:
                current_width = column_metadata[col].get("pixelSize", 100)
            except IndexError:
                current_width = 100  # default fallback

            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": col,
                        "endIndex": col + 1
                    },
                    "properties": {
                        "pixelSize": current_width + extra_pixels
                    },
                    "fields": "pixelSize"
                }
            })

        # Send the batch update
        SPREADSHEET_OPS.SERVICE.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_OPS.SPREADSHEET_ID,
            body={"requests": requests}
        ).execute()

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

    @staticmethod
    def get_team_data_from_json(json_file_path):
        """
        Load team data from a JSON file.
        [param] json_file_path: Path to the JSON file containing team data.
        [return] player_dict: Dictionary containing player data.
        """
        if not os.path.exists(json_file_path):
            error_print(f"JSON file '{json_file_path}' does not exist.")
            return {}

        try:
            with open(json_file_path, 'r') as file:
                player_dict = json.load(file)
            return player_dict
        except Exception as e:
            error_print(f"Error reading JSON file: {e}")
            return {}

    @staticmethod
    def a1_to_grid_coords(a1_notation):
        """
        Convert A1 notation (e.g., "A1", "B2", "Z10") to grid coordinates (column, row).
        [param] a1_notation: A1 notation string to convert.
        [return] (col, row): Tuple containing the column (0-based index) and row (0-based index).
        """
        match = re.match(r"([A-Z]+)(\d+)", a1_notation)
        if not match:
            raise ValueError(f"Invalid A1 notation: {a1_notation}")
        col_letters, row_number = match.groups()
        col = sum((ord(char) - 64) * (26 ** idx) for idx, char in enumerate(reversed(col_letters))) - 1
        row = int(row_number) - 1
        return col, row
    
    @staticmethod
    def generate_rank_score(rank_text):
        # splice first word
        rank_tier = rank_text.split(" ")[0] 
        rank_lp = "??" # default LP if not found
        if len(rank_text.split(" ")) > 2:
            rank_lp = rank_text.split(" ")[1] + rank_text.split(" ")[2]  # get the last 2 terms as LP
        
        rank_points = {
            "I4": 0,    "I3": 1,    "I2": 2,    "I1": 3,
            "B4": 4,    "B3": 5,    "B2": 6,    "B1": 7,
            "S4": 8,    "S3": 9,    "S2": 10,   "S1": 11,
            "G4": 12,   "G3": 13,   "G2": 14,   "G1": 15,
            "P4": 16,   "P3": 17,   "P2": 18,   "P1": 19,
            "E4": 20,   "E3": 21,   "E2": 22,   "E1": 23,
            "D4": 24,   "D3": 25,   "D2": 26,   "D1": 27,
            "M": 28,    "GM": 36,   "C": 42,    "??": -1,          # apex ranks averages
            "I": 1.5,   "B": 5.5,   "S": 9.5,   "G": 13.5,  "P": 17.5   # metal rank averages
        }

        print(f"Generating rank score for: {rank_text}")
        print(f"Rank tier: {rank_tier}, LP: {rank_lp}")
        print(f"Rank points: {rank_points.get(rank_tier, 0)}")

        if rank_lp != "??":
            # convert to integer and divide by 100
            rank_lp = int(rank_lp.replace("LP", "").replace("lp", "").strip()) / 100
            return rank_points[rank_tier] + rank_lp  # return the rank score with LP added (for apex ranks)
        else:
            return rank_points[rank_tier]

    @staticmethod
    def standardize_rank(rank_text):
        """
        Standardize the rank text to a common format.
        [param] rank_text: The rank text to standardize.
        [return] standardized_rank: The standardized rank text.
        """
        # take the first and last letter of the rank text
        standardized_rank_text = rank_text.strip().upper()
        standardized_rank = ""

        # check if starts with a letter from a list of given letters
        print(f"Standardizing rank text: {standardized_rank_text}")
        if standardized_rank_text.startswith(("IRON", "B", "S", "GOLD", "P", "E", "D")):
            standardized_rank = standardized_rank_text[0] + standardized_rank_text[-1]
        elif standardized_rank_text.startswith("M"):# the rest of the rank text is the LP
            standardized_rank = standardized_rank_text.replace("MASTER", "M", 1)
        elif standardized_rank_text.startswith("G"):
            standardized_rank = standardized_rank_text.replace("GRANDMASTER", "GM", 1)
        elif standardized_rank_text.startswith("C"):
            standardized_rank = standardized_rank_text.replace("CHALLENGER", "C", 1)
        else:
            standardized_rank = "??"

        return standardized_rank

    @staticmethod
    # Calculate ending column letter
    def col_letter_offset(col, offset):
        return chr(ord(col.upper()) + offset)