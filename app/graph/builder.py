from langgraph.graph import StateGraph, END
from app.schemas.state import AgentState
from app.nodes.transcribe_node import transcribe_node
from app.nodes.classify_node import classify_node
from app.nodes.extract_node import extract_node
from app.nodes.log_expense_node import log_expense_node
from app.nodes.fetch_summary_node import fetch_summary_node
from app.nodes.respond_node import respond_node
from app.nodes.analyze_node import analyze_spending_node
from app.nodes.validate_node import validate_node


def route_after_classify(state: AgentState) -> str:
    if state.intent == "log_expense":
        return "extract"
    elif state.intent == "summary_query":
        return "fetch_summary"
    elif state.intent == "analyze_spending":
        return "fetch_summary"  
    else:
        return "respond"
    
def route_after_summary(state: AgentState) -> str:
    if state.intent == "analyze_spending":
        return "analyze_spending"
    return "respond"

def route_after_validate(state: AgentState) -> str:
    if state.validated:
        return "log_expense"
    return "respond"



def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("transcribe", transcribe_node)
    graph.add_node("classify", classify_node)
    graph.add_node("extract", extract_node)
    graph.add_node("log_expense", log_expense_node)
    graph.add_node("fetch_summary", fetch_summary_node)
    graph.add_node("analyze_spending", analyze_spending_node)
    graph.add_node("respond", respond_node)
    graph.add_node("validate", validate_node)

    graph.set_entry_point("transcribe")
    graph.add_edge("transcribe", "classify")

    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "extract": "extract",
            "fetch_summary": "fetch_summary",
            "respond": "respond"
        }
    )

    graph.add_edge("extract", "validate")
    graph.add_conditional_edges(
    "validate",
    route_after_validate,
    {
        "log_expense": "log_expense",
        "respond": "respond",
    },
    )
    graph.add_edge("log_expense", "respond")
    graph.add_conditional_edges(
    "fetch_summary",
    route_after_summary,
    {
        "analyze_spending": "analyze_spending",
        "respond": "respond"
    }
)
    graph.add_edge("analyze_spending", "respond")
    graph.add_edge("respond", END)

    return graph.compile()