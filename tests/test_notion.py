from app.services.notion_service import create_expense_page

expense = {
    "amount": 20,
    "category": "Food",
    "merchant": "Chipotle",
    "date": "2026-04-07",
    "notes": "Lunch"
}

result = create_expense_page(expense)
print(result)