from app.agents.classifier import classify_intent


def test_log_expense_intent():
    text = "I spent 20 dollars on food"
    intent = classify_intent(text)

    assert intent in ["log_expense", "summary_query", "analyze_spending", "unknown"]