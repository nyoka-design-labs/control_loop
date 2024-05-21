import gspread
from google.oauth2.service_account import Credentials

# Initialize the Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
SERVICE_ACCOUNT_FILE = '/Users/mba_sam/Github/Nyoka Design Labs/control_loop/src/sheets_access_key.json'  # Update this path

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

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
    Saves the data to a Google Sheet. Creates the sheet if it doesn't exist.
    Parameters:
        data (list of lists): The data to save.
        headers (list): The headers for the data.
        sheet_name (str): The name of the Google Sheet.
        emails_to_share (list): List of email addresses to share the sheet with.
    Returns:
        None
    """
    # Clean the data before saving
    data = clean_data(data)
    # emails_to_share = ["daniel@lightbynyoka.com", "charf@lightbynyoka.com"]
    emails_to_share = ["samgupta.1738@gmail.com"]
 
    # Try to open the existing spreadsheet
    spreadsheet = client.open(sheet_name)
    print(f"Opened existing sheet: {sheet_name}")
    

    # Check existing permissions and share only with new emails
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
        else:
            print(f"Sheet already shared with: {email}")

    # Select the first sheet
    sheet = spreadsheet.sheet1

    # Get all values from the sheet
    existing_data = sheet.get_all_values()

    # Check if headers are present
    if not existing_data or existing_data[0] != headers:
        # If headers are not present, insert headers at the first row
        sheet.insert_row(headers, 1)
        print("Inserted headers")

    # Append the new data after the existing data
    start_row = len(existing_data) + 1 if existing_data else 2
    for row in data:
        sheet.insert_row(row, start_row)
        start_row += 1

    print("Appended data to the sheet")

if __name__ == "__main__":
    data = [
        ["John Doe", "john@example.com", "1234567890"],
        ["Jane Smith", "jane@example.com", "0987654321"]
    ]
    headers = ["Name", "Email", "Phone"]
    sheet_name = "Contact Information"
    

    save_to_sheet(data, headers, sheet_name)
