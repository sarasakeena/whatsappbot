import base64

with open("whatsappbot-463107-0fea5ed4b30e.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print(encoded)
