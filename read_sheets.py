import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import json
import base64

# Decode credentials from secrets
GOOGLE_CREDS = json.loads(base64.b64decode(st.secrets["GOOGLE_CREDS"]))
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(GOOGLE_CREDS, scopes=scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

# Get all records
data = sheet.get_all_records()

# Display data
for row in data:
    print(row["Name"], row["Phone Number"], row["Message"], row["Date"], row["Time"])
