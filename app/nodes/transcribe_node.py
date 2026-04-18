from app.schemas.state import AgentState


def transcribe_node(state: AgentState) -> AgentState:
    state.execution_path.append("transcribe")
    if state.user_input:
        state.transcribed_text = state.user_input
        
    return state