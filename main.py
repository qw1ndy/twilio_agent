import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay
from google import genai
from google.genai import types

from agent.llm_handler import make_llm_request

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

NGROK_URL = str(os.getenv("NGROK_URL"))

app = FastAPI()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.post("/call", response_class=Response)
async def make_call_and_get_twiml():
    print("Received request /call, generating TwiML...")

    response = VoiceResponse()
    connect = Connect()

    conversationrelay = ConversationRelay(
        url=f"wss://{NGROK_URL.split('//')[1]}/ws",
    )

    conversationrelay.language(
        code="en-US",
        tts_provider="ElevenLabs",
        voice="UgBBYS2sOqTuMpoF3BR0",
        transcription_provider="Deepgram",
        speech_model="nova-2-general",
    )

    connect.append(conversationrelay)
    response.append(connect)

    return Response(content=str(response), media_type="application/xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket connection is established.")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            msg_type = data.get("type")

            if msg_type == "setup":
                print("ℹ️ Setup received. Sending initial greeting.")

                ai_response_text = await make_llm_request("Start the dialog")
                print(ai_response_text)
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": ai_response_text,
                    "last": True,
                    "interruptible": True
                }))
                continue

            if msg_type == "prompt":
                user_input = data.get("voicePrompt", "")
                print(f"👤 User said: {user_input}")

                if not user_input.strip():
                    continue

                ai_response_text = await make_llm_request(user_input)
                print(f"🤖 AI reply: {ai_response_text}")

                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": ai_response_text,
                    "last": True,
                    "interruptible": True
                }))

            if msg_type == "error":
                print(f"⚠️ Error message received from Twilio: {data.get('description')}")


    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
            print("🔌 WebSocket connection closed.")
        except Exception as e:
            print(f"Websocket connection already closed: {e}")


def initiate_outbound_call():
    print(f"Initiates an outbound call via {TWILIO_PHONE_NUMBER} to {RECIPIENT_PHONE_NUMBER}")
    try:
        call = client.calls.create(
            to=RECIPIENT_PHONE_NUMBER,  # type: ignore
            from_=TWILIO_PHONE_NUMBER,  # type: ignore
            url=f"{NGROK_URL}/call"
        )
        print(f"The call was successfully initiated. Call SID: {call.sid}")
    except Exception as e:
        print(f"Failed to initiate call: {e}")

if __name__ == "__main__":
    import uvicorn

    initiate_outbound_call()
    uvicorn.run(app, host="0.0.0.0", port=8000)