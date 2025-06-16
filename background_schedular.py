import schedule 
import time
import gspread
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime
import os
import json
import base64

# --- Load environment variables ---
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
GOOGLE_CREDS = os.environ.get("GOOGLE_CREDS")

# --- Setup Twilio ---
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# --- Setup Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
json_creds = json.loads(base64.b64decode(GOOGLE_CREDS).decode("utf-8"))
creds = Credentials.from_service_account_info(json_creds, scopes=scope)
client_sheets = gspread.authorize(creds)
sheet = client_sheets.open("WhatsAppReminders").sheet1

def send_scheduled_messages():
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    try:
        data = sheet.get_all_records()
        for row in data:
            if row["Date"] == current_date and row["Time"] == current_time:
                try:
                    client.messages.create(
                        body=row["Message"],
                        from_=TWILIO_WHATSAPP_NUMBER,
                        to=f"whatsapp:{row['Phone Number']}"
                    )
                    print(f"✅ Sent to {row['Name']} ({row['Phone Number']})")
                except Exception as e:
                    print(f"❌ Failed to send to {row['Name']}: {e}")
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")

# Schedule it every minute
schedule.every(1).minutes.do(send_scheduled_messages)

print("💬 WhatsApp Auto Scheduler Started...")
while True:
    schedule.run_pending()
    time.sleep(1)
