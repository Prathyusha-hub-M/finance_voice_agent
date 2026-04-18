from app.schemas.state import AgentState
from app.agents.responder import (
    build_log_response,
    build_summary_response,
    build_error_response,
)


def respond_node(state: AgentState) -> AgentState:
    state.execution_path.append("respond")
    if state.errors:
        state.response = build_error_response(state.errors[-1])
        return state

    # If response already exists (from analyze node), just return
    if state.response:
        return state

    if state.intent == "log_expense" and state.expense:
        state.response = build_log_response(state.expense)

    elif state.intent == "summary_query" and state.summary_result:
        state.response = build_summary_response(state.summary_result)

    else:
        state.response = "I understood your request, but I could not complete the workflow."

    return state