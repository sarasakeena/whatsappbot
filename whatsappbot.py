import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
import json
import base64

# --- ENV SETUP ---
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")

if not GOOGLE_CREDS:
    st.error("❌ GOOGLE_CREDS environment variable not set.")
    st.stop()

# --- TWILIO SETUP ---
client_twilio = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    json_creds = json.loads(base64.b64decode(os.getenv(GOOGLE_CREDS)))
    creds = Credentials.from_service_account_info(json_creds, scopes=scope)
    client_sheets = gspread.authorize(creds)
    sheet = client_sheets.open("WhatsAppReminders").sheet1
except Exception as e:
    st.error(f"❌ Failed to authorize Google Sheets: {e}")
    st.stop()

# --- STREAMLIT UI ---
st.set_page_config(page_title="WhatsApp Scheduler", page_icon="💬")
st.title("💬 WhatsApp Message Scheduler (Abzuna)")

# Message scheduler input
with st.form("schedule_form"):
    st.markdown("### ✍️ Schedule New Message")
    name = st.text_input("Name")
    phone = st.text_input("Phone Number (e.g., 91XXXXXXXXXX)")
    message = st.text_area("Message")
    date = st.date_input("Date")
    time = st.time_input("Time")

    submit = st.form_submit_button("📤 Schedule")

    if submit:
        if name and phone and message:
            try:
                sheet.append_row([name, phone, message, date.strftime("%Y-%m-%d"), time.strftime("%H:%M")])
                st.success("✅ Message scheduled successfully!")
            except Exception as e:
                st.error(f"❌ Failed to schedule message: {e}")
        else:
            st.warning("⚠️ All fields are required!")

# --- SHOW EXISTING SCHEDULES ---
st.markdown("### 📄 Scheduled Messages")
try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No messages scheduled yet.")
except Exception as e:
    st.error(f"❌ Failed to fetch scheduled messages: {e}")

# --- SEND SCHEDULED MESSAGES ---
st.markdown("### 🚀 Send Messages Now")
if st.button("🧨 Check and Send Scheduled Messages"):
    try:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        sent_count = 0
        for row in data:
            if row["Date"] == current_date and row["Time"] == current_time:
                try:
                    client_twilio.messages.create(
                        body=row["Message"],
                        from_=TWILIO_WHATSAPP_NUMBER,
                        to=f"whatsapp:{row['Phone Number']}"
                    )
                    sent_count += 1
                    st.success(f"✅ Sent to {row['Name']} at {row['Phone Number']}")
                except Exception as e:
                    st.error(f"❌ Failed to send to {row['Name']}: {e}")

        if sent_count == 0:
            st.info("ℹ️ No messages scheduled for this exact time.")
    except Exception as e:
        st.error(f"❌ Error while checking/sending messages: {e}")
