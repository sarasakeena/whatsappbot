# 💬 WhatsApp Message Scheduler — Abzuna Automations

Welcome to **Abzuna Automations**, your AI-powered automation assistant for business productivity.

This project is a **WhatsApp Message Scheduler** built using:
- 🐍 Python
- 📊 Google Sheets
- 💬 Twilio WhatsApp API
- ⚡ Streamlit UI

##  Features

- Schedule WhatsApp messages for your customers using a web-based UI
- Automatically reads schedule data from Google Sheets
- Sends messages through Twilio’s WhatsApp API
- Manual trigger to send messages on the fly
- Secure .env configuration for secrets

## Tech Stack

| Tool      | Purpose                      |
|-----------|------------------------------|
| Python    | Backend logic & scheduling   |
| Streamlit | Frontend UI                  |
| Twilio    | WhatsApp message delivery    |
| GSpread   | Google Sheets integration    |
| dotenv    | Secure credentials handling  |


## 🔐 Setup Guide

1. Clone the repo
2. Create a `.env` file with your Twilio credentials:
    ```
    TWILIO_SID=your_sid
    TWILIO_AUTH_TOKEN=your_token
    TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
    ```

3. Add your `credentials.json` from Google Cloud
4. Create a Google Sheet named **"WhatsAppReminders"** with columns:
    ```
    Name | Phone Number | Message | Date | Time
    ```
5. Run the app:
    ```
    streamlit run app.py
    ```

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.

## 👤 Author

**Sara Sakeena **  
Founder — [Abzuna Automations](https://github.com/yourusername)

---

### 📨 Need a WhatsApp bot for your business?

Contact us at `sarasakeena@gmail.com` or DM [@abzuna.tech](https://instagram.com/abzuna.tech)

