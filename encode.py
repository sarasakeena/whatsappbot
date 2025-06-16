import base64

with open("whatsappbot-463107-00da22f31abf.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print(encoded)
