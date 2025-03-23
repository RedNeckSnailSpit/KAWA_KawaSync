from modules.config import Config
from modules.database import Database
from modules.google import GoogleSheets
import modules.constants as constants

# Initialize database connection
name_version_str = f"{constants.SCRIPT_NAME} v{constants.VERSION}"
box_width = len(name_version_str) + 2
print("+" + "-" * (box_width) + "+")
print("| " + name_version_str + " |")
print("+" + "-" * (box_width) + "+")

config = Config()
db = Database(config.get("database"))
db.connect()

# Initialize Google Sheets instance
google_sheets = GoogleSheets(credentials_file="credentials.json", file_id="10GLtvQqgf2SL6gpFKoGLiPRt1MyzUYzghsGCBmaLlU4")

# Fetch pricing and shipping data from Google Sheets
pricing_data = google_sheets.fetch_data(sheet_name="Prices")
shipping_data = google_sheets.fetch_data(sheet_name="Shipping")

# Parse and update the database with fetched data
db.parse_and_update_pricing_data(pricing_data)
db.parse_and_update_shipping_data(shipping_data)

db.close()
