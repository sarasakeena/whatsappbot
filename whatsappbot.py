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
    message = st.text_area("Message to Send")
    
    date_input = st.text_input("Date (YYYY-MM-DD)")
    time_input = st.text_input("Time (HH:MM in 24-hour format)")
    
    payment_status = st.selectbox("Have you paid the ₹68 subscription?", ["No", "Yes (Just Now)"])

    submit = st.form_submit_button("📤 Schedule")

    if submit:
        if name and phone and message and date_input and time_input:
            try:
                # Validate datetime input
                try:
                    schedule_dt = datetime.strptime(f"{date_input} {time_input}", "%Y-%m-%d %H:%M")
                except ValueError:
                    st.error("❌ Invalid date/time format. Use YYYY-MM-DD and HH:MM.")
                    st.stop()

                now = datetime.now()
                current_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M")

                data = sheet.get_all_records()
                user_found = False
                for row in data:
                    if str(row["Phone Number"]) == phone:
                        user_found = True
                        trial_used = row.get("Trial Used", "").lower() == "yes"
                        subscribed = row.get("Subscribed", "").lower() == "yes"

                        # 🔁 Auto-subscribe if they selected payment done
                        if payment_status == "Yes (Just Now)":
                            subscribed = True
                            subscribed_status = "Yes"
                            last_payment_date = current_date
                        else:
                            subscribed_status = "Yes" if subscribed else "No"
                            last_payment_date = row.get("Last Payment Date", "")

                        # Check permission
                        if subscribed or not trial_used:
                            trial_status = "Yes"
                            sheet.append_row([
                                name, phone, message,
                                date_input, time_input,
                                trial_status, subscribed_status,
                                last_payment_date
                            ])

                            st.success("✅ Message scheduled successfully!")

                            # ✅ Immediately send the user's message
                            if date_input == current_date and time_input == current_time:
                                try:
                                    client_twilio.messages.create(
                                        body=message,
                                        from_=TWILIO_WHATSAPP_NUMBER,
                                        to=f"whatsapp:{phone}"
                                    )
                                    st.success("🚀 Message sent instantly!")
                                except Exception as e:
                                    st.error(f"❌ Failed to send instantly: {e}")

                            # ✅ Send confirmation message to user
                            try:
                                confirmation = f"Hi {name}, your message has been scheduled for {date_input} at {time_input}. Thank you for using Abzuna 💬"
                                client_twilio.messages.create(
                                    body=confirmation,
                                    from_=TWILIO_WHATSAPP_NUMBER,
                                    to=f"whatsapp:{phone}"
                                )
                            except Exception as e:
                                st.warning(f"⚠️ Could not send confirmation: {e}")

                        else:
                            st.warning("""
                            ❌ You've already used your 1-day free trial.

                            💰 To continue using this service:
                            - Pay ₹68/month  
                            - UPI ID: `sarasakeena@okaxis`  

                            ✅ Once paid, resubmit and select "Yes (Just Now)".
                            """)
                        break

                if not user_found:
                    trial_status = "Yes"
                    subscribed_status = "Yes" if payment_status == "Yes (Just Now)" else "No"
                    last_payment_date = current_date if payment_status == "Yes (Just Now)" else ""

                    sheet.append_row([name, phone, message, date_input, time_input, trial_status, subscribed_status, last_payment_date])
                    st.success("🎉 Trial activated! Message scheduled.")

                    # ✅ Immediately send the user's message if date/time match
                    if date_input == current_date and time_input == current_time:
                        try:
                            client_twilio.messages.create(
                                body=message,
                                from_=TWILIO_WHATSAPP_NUMBER,
                                to=f"whatsapp:{phone}"
                            )
                            st.success("🚀 Message sent instantly!")
                        except Exception as e:
                            st.error(f"❌ Failed to send instantly: {e}")

                    # ✅ Send confirmation message to user
                    try:
                        confirmation = f"Hi {name}, your message has been scheduled for {date_input} at {time_input}. Thank you for using Abzuna 💬"
                        client_twilio.messages.create(
                            body=confirmation,
                            from_=TWILIO_WHATSAPP_NUMBER,
                            to=f"whatsapp:{phone}"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Could not send confirmation: {e}")

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
