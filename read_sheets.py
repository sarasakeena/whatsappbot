import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Setup access
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet
sheet = client.open("WhatsAppReminders").sheet1  # change the sheet name
data = sheet.get_all_records()

# Show the data
for row in data:
    print(row["Name"], row["Phone Number"], row["Message"], row["Date"], row["Time"])
