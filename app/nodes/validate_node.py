from app.schemas.state import AgentState, ValidationError
from app.services.validator import validate_expense_data
from app.utils.logger import log_event



def validate_node(state: AgentState) -> AgentState:
    state.execution_path.append("validate")
    log_event(state, "validate", "start")

    try:
        is_valid, error = validate_expense_data(state.expense)

     
        state.validated = is_valid
        state.validation_error = error

        if error:
            state.errors.append(error.message)
            log_event(state, "validate", f"failed: {error.type}")
        else:
            log_event(state, "validate", "success")

    #     print(
    #         f"[NODE] validate - valid={state.validated}, "
    #         f"error={error.message if error else None}"  )

    except Exception as e:
        state.validated = False

        validation_error = ValidationError(
            type="validation_exception",
            message=str(e)
        )

        state.validation_error = validation_error
        state.errors.append(validation_error.message)

        #print(f"[ERROR] validate: {str(e)}")
        log_event(state, "validate", f"exception: {str(e)}")

    return state