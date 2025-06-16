from twilio.rest import Client # type: ignore

account_sid = 'ACb9b05407a59db64ab49840aaef33b348'
auth_token = '15d8e4c1d5f4c39c767eb84ae2da47c5'
client = Client(account_sid, auth_token)

message = client.messages.create(
    body="👋 Reminder: Your appointment is at 4 PM today!",
    from_='whatsapp:+14155238886',  # Twilio WhatsApp number
    to='whatsapp:+917305958242'
)

print(f"Message sent: {message.sid}")
