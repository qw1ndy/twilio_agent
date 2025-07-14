from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay
import os
from dotenv import load_dotenv

load_dotenv()
NGROK_URL = str(os.getenv("NGROK_URL"))

def generate_twiml():
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