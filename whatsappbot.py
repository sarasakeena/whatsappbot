import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime
import pandas as pd
import json
import base64
import os

# --- ENV SETUP ---
TWILIO_SID = os.environ["TWILIO_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_NUMBER = os.environ["TWILIO_WHATSAPP_NUMBER"]
GOOGLE_CREDS = os.environ["GOOGLE_CREDS"]

# --- TWILIO SETUP ---
client_twilio = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    json_creds = json.loads(base64.b64decode(GOOGLE_CREDS).decode("utf-8"))
    creds = Credentials.from_service_account_info(json_creds, scopes=scope)
    client_sheets = gspread.authorize(creds)
    sheet = client_sheets.open("WhatsAppReminders").sheet1
except Exception as e:
    st.error(f"❌ Failed to authorize Google Sheets: {e}")
    st.stop()

# --- UI CONFIG ---
st.set_page_config(page_title="WhatsApp Scheduler", page_icon="💬")
st.title("💬 WhatsApp Message Scheduler (Abzuna)")

st.markdown("""
💬 **Usage Policy**
- ✅ One-time **1-day free trial**
- 💰 ₹68/month for full access
- 📲 UPI: `sarasakeena@okaxis`

🧾 After payment, we'll activate your subscription manually.
""")

# --- FORM ---
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
            data = sheet.get_all_records()
            user_found = False
            for row in data:
                if str(row["Phone Number"]) == phone:
                    user_found = True
                    trial_used = row.get("Trial Used", "").lower() == "yes"
                    subscribed = row.get("Subscribed", "").lower() == "yes"

                    if subscribed:
                        sheet.append_row([name, phone, message, date.strftime("%Y-%m-%d"), time.strftime("%H:%M"), "Yes", "Yes", row.get("Last Payment Date", "")])
                        st.success("✅ Message scheduled successfully! (Subscribed User)")
                    elif not trial_used:
                        sheet.append_row([name, phone, message, date.strftime("%Y-%m-%d"), time.strftime("%H:%M"), "Yes", "No", ""])
                        st.success("✅ Trial used! Your message is scheduled.")
                    else:
                        st.warning("""  
                            ❌ You’ve already used your 1-day free trial.  

                            💰 To continue using this service:  
                            - Pay ₹68/month  
                            - UPI ID: `sarasakeena@okaxis`

                            ✅ Once paid, we’ll activate your subscription manually.
                        """)
                    break

            if not user_found:
                # New user – allow 1-day free trial
                sheet.append_row([name, phone, message, date.strftime("%Y-%m-%d"), time.strftime("%H:%M"), "Yes", "No", ""])
                st.success("🎉 Welcome! Trial activated. Message scheduled.")
        except Exception as e:
            st.error(f"❌ Failed to schedule message: {e}")
    else:
        st.warning("⚠️ All fields are required!")


# --- DISPLAY EXISTING MESSAGES ---
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

# --- SENDING LOGIC ---
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
            st.info("ℹ️ No messages to send right now.")
    except Exception as e:
        st.error(f"❌ Error while sending messages: {e}")
