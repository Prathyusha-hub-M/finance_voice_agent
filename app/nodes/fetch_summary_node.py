from app.schemas.state import AgentState
from app.services.notion_service import sum_recent_expenses
from app.utils.logger import log_event


def process_summary(summary: dict) -> dict:
    items = summary.get("items", [])

    category_totals = {}

    for item in items:
        category = item.get("category", "Other")
        amount = item.get("amount", 0)

        category_totals[category] = category_totals.get(category, 0) + amount

    total = summary.get("total", 0.0)

    return {
        "total": total,
        "category_breakdown": category_totals,
        "items": items[:5]  # limit for LLM
    }


def fetch_summary_node(state: AgentState) -> AgentState:
    state.execution_path.append("fetch_summary")
    log_event(state, "fetch_summary", "start")


    try:
        print("[NODE] fetch_summary - start")

        raw_summary = sum_recent_expenses()

        #print("[DEBUG] RAW SUMMARY:", raw_summary)
        log_event(state, "fetch_summary", f"raw_total={raw_summary.get('total')}")


        processed_summary = process_summary(raw_summary)

        state.summary_result = processed_summary

        #print("[DEBUG] PROCESSED SUMMARY:", processed_summary)
        log_event(state, "fetch_summary", "success")


    except Exception as e:
        state.errors.append(str(e))
        #print("[ERROR] fetch_summary:", str(e))
        log_event(state, "fetch_summary", f"error={str(e)}")
    return state