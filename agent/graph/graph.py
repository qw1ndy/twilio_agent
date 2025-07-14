from langgraph.graph import StateGraph, END
from utils.state import ConversationState
from .nodes import ai_response, extract_info_node, should_end

def build_graph():
    builder = StateGraph(ConversationState)
    builder.add_node("ai", ai_response)
    builder.add_node("extract", extract_info_node)
    builder.set_entry_point("ai")
    builder.add_edge("ai", "extract")
    builder.add_conditional_edges("extract", should_end, {
        "continue": "ai",
        "end": END
    })

    app = builder.compile()

    app.get_graph().draw_mermaid_png(output_file_path="flow.png")

    return app
