from utils.state import ConversationState
from agent.llm.llm_handler import extract_info, llm
from utils.promts import system_prompt


def ai_response(state: ConversationState) -> ConversationState:
    history = state["history"]
    info = state["info"]

    if info.name:
        reply = info.name
    else:
        full_prompt = system_prompt + "\n\nConversation so far:\n" + "\n".join(history)
        reply = llm.predict(full_prompt).strip()

    history.append(f"AI: {reply}")
    return {"history": history, "info": info}


def human_response(state: ConversationState, user_input: str) -> ConversationState:
    state["history"].append(f"Human: {user_input}")
    return state


def extract_info_node(state: ConversationState) -> ConversationState:
    parsed = extract_info(state["history"])
    return {"history": state["history"], "info": parsed}


def should_end(state: ConversationState) -> str:
    info = state["info"]
    if info.name and info.agreed_to_coffee:
        return "end"
    return "continue"
