from app.services.llm import llm


def classify_intent(text: str) -> str:
    prompt = f"""
You are an intent classifier for a finance assistant.

Your job is to classify the user's intent into ONE of the following:

- log_expense → user is recording a transaction
- summary_query → user is asking for past spending data
- analyze_spending → user wants insights, trends, or advice
- unknown → anything else

Rules:
- If user mentions spending money → log_expense
- If user asks for totals/history → summary_query
- If user asks for insights/advice/trends → analyze_spending

Examples:
"I spent 20 dollars on lunch" → log_expense
"Spent 45 on Uber" → log_expense
"How much did I spend?" → summary_query
"Show my recent expenses" → summary_query
"Analyze my spending" → analyze_spending
"Where am I spending the most?" → analyze_spending
"How can I save money?" → analyze_spending

User input:
{text}

Return ONLY one label:
log_expense | summary_query | analyze_spending | unknown
"""

    result = llm.invoke(prompt)
    content = result.content

    # normalize 
    if isinstance(content, list):
        content = content[0]

    content = str(content).strip().lower()

    # guardrail 
    if content not in {"log_expense", "summary_query", "analyze_spending", "unknown"}:
        return "unknown"

    return content