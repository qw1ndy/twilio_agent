import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
NGROK_URL = os.getenv("NGROK_URL")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def end_call(call_sid: str):
    try:
        client.calls(call_sid).update(status="completed")
        print(f"✅ Call {call_sid} ended.")
    except Exception as e:
        print(f"❌ Failed to end call {call_sid}: {e}")

def initiate_call():
    try:
        call = client.calls.create(
            to=RECIPIENT_PHONE_NUMBER, #type: ignore
            from_=TWILIO_PHONE_NUMBER, #type: ignore
            url=f"{NGROK_URL}/call"
        )
        print(f"📞 Call initiated: {call.sid}")
    except Exception as e:
        print(f"❌ Failed to initiate call: {e}")