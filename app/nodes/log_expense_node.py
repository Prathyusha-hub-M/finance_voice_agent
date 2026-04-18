from app.schemas.state import AgentState
from app.services.notion_service import create_expense_page


def log_expense_node(state: AgentState) -> AgentState:
    state.execution_path.append("log_expense")
    try:
        if state.expense is None:
            raise ValueError("No expense found to log.")

        state.notion_result = create_expense_page(state.expense.model_dump())
        
    except Exception as e:
        state.errors.append(str(e))
    return state