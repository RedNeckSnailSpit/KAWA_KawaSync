import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheets:
    """A class for interacting with Google Sheets."""

    def __init__(self, credentials_file, file_id):
        """
        Initialize the GoogleSheets instance.
        :param credentials_file: Path to the Google Sheets API credentials JSON file.
        :param file_id: Google Sheets file ID.
        """
        self.credentials_file = credentials_file
        self.file_id = file_id

    def fetch_data(self, sheet_name):
        """
        Fetch data from a specific Google Sheet.
        :param sheet_name: Name of the worksheet to fetch data from.
        :return: 2D list representing sheet data.
        """
        try:
            # Setup Google Sheets API scope and credentials
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
            client = gspread.authorize(creds)

            # Open the worksheet and fetch all values
            sheet = client.open_by_key(self.file_id).worksheet(sheet_name)
            print(f"Opened Worksheet: {sheet_name}")
            return sheet.get_all_values()
        except Exception as e:
            raise RuntimeError(f"Error fetching Google Sheets data for {sheet_name}: {e}")
