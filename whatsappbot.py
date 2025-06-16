import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd

# --- ENV SETUP ---
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client_twilio = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client_sheets = gspread.authorize(creds)
sheet = client_sheets.open("WhatsAppReminders").sheet1

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
            sheet.append_row([name, phone, message, date.strftime("%Y-%m-%d"), time.strftime("%H:%M")])
            st.success("✅ Message scheduled successfully!")
        else:
            st.warning("⚠️ All fields are required!")

# --- SHOW EXISTING SCHEDULES ---
st.markdown("### 📄 Scheduled Messages")
data = sheet.get_all_records()
df = pd.DataFrame(data)
if not df.empty:
    st.dataframe(df)
else:
    st.info("No messages scheduled yet.")

# --- SEND SCHEDULED MESSAGES (MANUAL TRIGGER) ---
st.markdown("### 🚀 Send Messages Now")
if st.button("🧨 Check and Send Scheduled Messages"):
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
