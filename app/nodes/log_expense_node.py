from app.schemas.state import AgentState
from app.services.notion_service import create_expense_page
from app.utils.logger import log_event


def log_expense_node(state: AgentState) -> AgentState:
    state.execution_path.append("log_expense")
    log_event(state, "log_expense", "start")
    try:
        if state.expense is None:
            raise ValueError("No expense found to log.")

        state.notion_result = create_expense_page(state.expense.model_dump())
        log_event(state, "log_expense", "success")
    except Exception as e:
        state.errors.append(str(e))
        log_event(
        state,
        "log_expense",
        f"exception: {str(e)}",
        level="error"
    )
    return state