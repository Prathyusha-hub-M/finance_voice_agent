from datetime import datetime, timezone
from pydantic import ValidationError
from app.services.llm import llm
from app.schemas.expense import Expense


def extract_expense(text: str) -> Expense:
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()

    prompt = f"""
Extract expense information from the user input.

Return valid JSON with this exact schema, do not include any explanation or text.
{{
  "amount": float,
  "category": "string",
  "merchant": "string or null",
  "date": "YYYY-MM-DD",
  "notes": "string or null"
}}

Rules:
- category must be one of: Food, Transport, Shopping, Bills, Entertainment, Health, Grocery
- If category unclear → use "Other"
- if date is missing, use {today}
- amount must be numeric only
- merchant should be short and clean
- notes can be null

User input:
{text}

Return only JSON.
"""
    result = llm.invoke(prompt)
    content = result.content

    if not isinstance(content, str):
        content = str(content)

    try:
        return Expense.model_validate_json(content)
    except ValidationError as e:
        raise ValueError(f"Failed to parse expense JSON: {e}")