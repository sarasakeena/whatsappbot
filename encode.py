import base64

with open("whatsappbot-463107-c6d0e1e6f9d0.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print(encoded)
