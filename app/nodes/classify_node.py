from app.schemas.state import AgentState
from app.agents.classifier import classify_intent
from app.utils.logger import log_event


def classify_node(state: AgentState) -> AgentState:
    state.execution_path.append("classify")
    
    try:
        state.intent = classify_intent(state.transcribed_text or "")
        log_event(state, "classify", f"intent={state.intent}")
        
    except Exception as e:
        state.errors.append(str(e))
        state.intent = "unknown"
    return state