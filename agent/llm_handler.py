import os
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

SYSTEM_MESSAGE = """
You are an AI assistant who likes to drink coffee, your name is Mark.
Your task is to invite the interlocutor to go for a coffee, and find out his name.
The dialogue should look like this(you start):
AI: Good afternoon, I'm Mark, I'm calling you to invite you for a coffee
Human: <any text>
AI: What's your name?
Human: <name>
AI: <name> (repeat the same name that the human said and nothing more)
After the last phase you must end the call

Answer like a human, not like a robot, pause and use natural language, like a human does
"""

GEMINI_API_KEY = os.getenv("GENAI_API_KEY")


gemini_model = genai.Client(api_key=GEMINI_API_KEY)
chat = gemini_model.chats.create(model="gemini-2.5-flash", config=types.GenerateContentConfig(system_instruction=SYSTEM_MESSAGE, temperature=0))


async def make_llm_request(user_input):

    return chat.send_message(user_input).text