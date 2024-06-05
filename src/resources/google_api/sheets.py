import gspread
from google.oauth2.service_account import Credentials
import os
from resources.utils import *
import traceback
from resources.logging_config import logger

# Define the scope of the API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Path to the service account key file
curr_directory = os.path.dirname(__file__)
SERVICE_ACCOUNT_FILE = os.path.join(curr_directory, 'sheets_access_key.json')

# Authenticate using the service account credentials
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

def clean_data(data):
    """
    Cleans the provided data by replacing infinite values and filling with N/A.
    Parameters:
        data (list of lists): The data to clean.
    Returns:
        list of lists: The cleaned data.
    """
    cleaned_data = []
    for row in data:
        cleaned_row = ["N/A" if val in [float('inf'), float('-inf'), None] else val for val in row]
        cleaned_data.append(cleaned_row)
    return cleaned_data

def save_to_sheet(data, headers, sheet_name):
    """
    Saves the data to a Google Sheet. If the sheet does not exist, raises an error.
    Parameters:
        data (list): The data to save.
        headers (list): The headers for the data.
        sheet_name (str): The name of the Google Sheet.
    Returns:
        None
    """
    # Emails to share the sheet with
    emails_to_share = ["samgupta.1738@gmail.com", "daniel@lightbynyoka.com", "tatiana@lightbynyoka.com", "svhahn1@gmail.com", "charf@lightbynyoka.com"]
    # emails_to_share = ["samgupta.1738@gmail.com"]

    # Try to open the existing spreadsheet by name
    spreadsheet = client.open(sheet_name)

    # Get existing permissions and share only with new emails
    existing_permissions = client.list_permissions(spreadsheet.id)
    existing_emails = [perm['emailAddress'] for perm in existing_permissions if 'emailAddress' in perm]

    for email in emails_to_share:
        if email not in existing_emails:
            client.insert_permission(
                spreadsheet.id,
                email,
                perm_type='user',
                role='writer'
            )
            print(f"Shared the sheet with: {email}")

    # Select the first sheet in the spreadsheet
    sheet = spreadsheet.sheet1

    # Get all existing data from the sheet
    existing_data = sheet.get_all_values()
    print(f"headers from the sheet: {existing_data[0]}")
    print(f"headers given: {headers}")
    # Check if headers are present, insert them if they are not
    if not existing_data or existing_data[0] != headers:
        sheet.insert_row(headers, 1)
        print("Inserted headers")

    # Append the new data after the existing data
    sheet.append_row(data)
    print("Added data to the sheet")

def save_dict_to_sheet(data, sheet_name):
    """
    Saves the data to a Google Sheet. If the sheet does not exist, raises an error.
    Parameters:
        data (dict): The data to save.
        sheet_name (str): The name of the Google Sheet.
    Returns:
        None
    """
    try:
        # Extract headers from the dictionary keys
        headers = list(data.keys())
        
        # Convert the dictionary to a list in the order of the headers
        data_list = [data.get(header, "") for header in headers]

        # Emails to share the sheet with
        emails_to_share = ["samgupta.1738@gmail.com", "daniel@lightbynyoka.com", "tatiana@lightbynyoka.com", "svhahn1@gmail.com", "charf@lightbynyoka.com"]
        # emails_to_share = ["samgupta.1738@gmail.com"]
        # Try to open the existing spreadsheet by name
        spreadsheet = client.open(sheet_name)

        # Get existing permissions and share only with new emails
        existing_permissions = client.list_permissions(spreadsheet.id)
        existing_emails = [perm['emailAddress'] for perm in existing_permissions if 'emailAddress' in perm]

        for email in emails_to_share:
            if email not in existing_emails:
                client.insert_permission(
                    spreadsheet.id,
                    email,
                    perm_type='user',
                    role='writer'
                )
                print(f"Shared the sheet with: {email}")

        # Select the first sheet in the spreadsheet
        sheet = spreadsheet.sheet1

        # Get all existing data from the sheet
        existing_data = sheet.get_all_values()
        if existing_data:
            sheet_headers = existing_data[0]
        else:
            sheet_headers = []

        # print(f"headers from the sheet: {sheet_headers}")
        # print(f"headers given: {headers}")

        # Check if headers are present, insert them if they are not
        if not existing_data or sheet_headers != headers:
            sheet.insert_row(headers, 1)
            print("Inserted headers")

        # Append the new data after the existing data
        sheet.append_row(data_list)
        print("Added data to the sheet")
    except Exception as e:
        print(f"failed to save data to sheets: \n{data}, \n{e}")
        logger.error(f"Error in save_dict_to_sheet: {e}\n{traceback.format_exc()}")
if __name__ == "__main__":
    # Example data and headers
    data = [100.254, 6.805, 21.567, 238.9, 0.0, 0.0, 0, 'data', 1716397226.4900506]
    headers = ['do', 'ph', 'temp', 'feed_weight', 'lactose_weight', 'base_weight', 'time', 'type', 'start_time']
    sheet_name = "fermentation_05-21-2024"

    # Save data to the sheet
    save_to_sheet(data, headers, sheet_name)
