from typing import Optional
from app.schemas.expense import Expense


def build_log_response(expense: Expense) -> str:
    merchant = f" at {expense.merchant}" if expense.merchant else ""
    return (
        f"Logged your expense of ${expense.amount:.2f} for {expense.category}{merchant} "
        f"on {expense.date}."
    )


def build_summary_response(summary: dict) -> str:
    total = summary.get("total", 0.0)
    items = summary.get("items", [])

    if not items:
        return "I could not find any recent expenses in Notion."

    lines = [f"Your recent total spending is ${total:.2f}. Recent expenses:"]
    for item in items[:5]:
        lines.append(
            f"- {item['merchant']}: ${item['amount']:.2f} ({item['category']})"
        )
    return "\n".join(lines)


def build_error_response(message: Optional[str] = None) -> str:
    return message or "Something went wrong while processing your request."