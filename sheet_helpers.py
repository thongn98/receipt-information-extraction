#Imports from python built-in modules
from __future__             import print_function

import pickle
import os.path

#Imports from 3rd parties
from googleapiclient.discovery      import build
from google_auth_oauthlib.flow      import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_RANGE_NAME = 'Sheet1!A:E'

def append(sheet_id, service, to_be_append):
    """
        Append processed receipts' information into google sheet with the provided credentials

        Parameters:
            sheet_id        : string
                ID of the google sheet to be modified
            service         : Google service
                service (role) to use for sheet modification
            to_be_append    : list
                list of info to be appended to the sheet
    """
    # Call the Sheets API
    sheet   = service.spreadsheets()
    values  = []
    for receipt in to_be_append:
        value = [receipt["image"], receipt["company"], receipt["address"], receipt["date"], receipt["total"]]
        values.append(value)

    body = {
        'values': values
    }

    result = service.spreadsheets().values().append(
    spreadsheetId=sheet_id, valueInputOption='USER_ENTERED', range=SAMPLE_RANGE_NAME, body=body).execute()
    return result

def create_sheet(name, service):
    """
        Create a google sheet with the provided name and credentials

        Parameters:
            name: string
                name of the sheet to be created
            service: Google service
                service (role) to use for sheet creation
        
        Return:
            string
                The id of the created Google sheet
    """
    spreadsheet     = {
        'properties': {
            'title': name
            }
    }
    spreadsheet     = service.spreadsheets().create(body=spreadsheet,
                                        fields='spreadsheetId').execute()
    spreadsheet_id  = spreadsheet.get('spreadsheetId')
    values          = [
        [
            "Image",
            "Company",
            "Address",
            "Date",
            "Total"
        ]
    ]
    body            = {
        'values': values
    }

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, valueInputOption='USER_ENTERED', range=SAMPLE_RANGE_NAME, body=body).execute()

    return spreadsheet_id

def init():
    """
        Initialize google sheet api

        Return:
            Google service
                service (role) to use for sheet creation and modification
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)

    return service