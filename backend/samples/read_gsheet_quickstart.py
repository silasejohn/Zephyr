import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# on scope change, delete config/token.json + re-run
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1ur1YDOgna2lsHO6ESRgpxgfBNHxpdVsjqqg9812qJHs"
SAMPLE_SHEET_NAME = "[TO] Nova Crystallis"
SAMPLE_SHEET_RANGE = "A2:Z"
SAMPLE_RANGE_NAME = f"{SAMPLE_SHEET_NAME}!{SAMPLE_SHEET_RANGE}" 

# Google Sample SID: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
# Google Sample Sheet Name / Range: Class Data!A2:E


# Personal Sample SID: 1ur1YDOgna2lsHO6ESRgpxgfBNHxpdVsjqqg9812qJHs
# Personal Sample Sheet Name / Range: [TO] Nova Crystallis!A2:F10

# if entire row empty, then will not print


def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("config/token.json"):
    creds = Credentials.from_authorized_user_file("config/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "config/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("config/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

    print("Name, Major:")
    for row in values:
      # Print All Columns 
      print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}")
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()