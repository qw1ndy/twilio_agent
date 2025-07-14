from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from utils.twilio_utils import initiate_call
from utils.twiml_generator import generate_twiml
from twilio_task.agent.graph.graph import build_graph
from utils.state import ConversationState, User_Info
from typing import cast
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
conversation_graph = build_graph()

@app.post("/call", response_class=Response)
async def make_call_and_get_twiml():
    return generate_twiml()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection is established.")

    state: ConversationState = {
        "history": [],
        "info": User_Info()
    }

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            msg_type = data.get("type")
            user_input = data.get("voicePrompt", "")

            if msg_type == "setup":
                result = conversation_graph.invoke(state)
                state = cast(ConversationState, result)
                response = state["history"][-1]

                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": response,
                    "last": True
                }))

            elif msg_type == "prompt":
                print(f"User said: {user_input}")

                state["history"].append(f"Human: {user_input}")

                result = conversation_graph.invoke(state)
                state = cast(ConversationState, result)

                response = state["history"][-1]
                print(f"🤖 Response: {response}")

                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": response,
                    "last": True
                }))

                if state["info"].name and state["info"].agreed_to_coffee:
                    print(f"Name: {state['info'].name}, Agreed: {state['info'].agreed_to_coffee}")
                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": state["info"].name,
                        "last": True
                    }))
                    await websocket.send_text(json.dumps({
                        "type": "end"
                    }))
                    break

            elif msg_type == "error":
                print(f"Error from Twilio: {data.get('description')}")

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
            print("WebSocket connection closed.")
        except Exception as e:
            print(f"WebSocket already closed: {e}")


if __name__ == "__main__":
    import uvicorn
    initiate_call()
    uvicorn.run(app, host="0.0.0.0", port=8000)
