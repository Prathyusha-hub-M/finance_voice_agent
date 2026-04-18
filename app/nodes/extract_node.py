from app.schemas.state import AgentState
from app.agents.extractor import extract_expense
from app.utils.logger import log_event


def extract_node(state: AgentState) -> AgentState:
    state.execution_path.append("extract")
    
    try:
        expense = extract_expense(state.transcribed_text or "")
        state.expense = expense
        log_event(state, "extract", f"amount={expense.amount}, category={expense.category}")
        

        # debug
        print("EXTRACTED:", expense)

    except Exception as e:
        state.errors.append(str(e))
        print("EXTRACTION ERROR:", str(e))

    return state