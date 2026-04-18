import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def create_expense_page(expense: dict) -> dict:
    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": expense.get("merchant") or expense.get("category") or "Expense"
                        }
                    }
                ]
            },
            "Amount": {
                "number": expense["amount"]
            },
            "Category": {
                "select": {
                    "name": expense["category"]
                }
            },
            "Merchant": {
                "rich_text": [
                    {
                        "text": {
                            "content": expense.get("merchant") or ""
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": expense.get("date") or datetime.utcnow().date().isoformat()
                }
            },
            "Notes": {
                "rich_text": [
                    {
                        "text": {
                            "content": expense.get("notes") or ""
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=NOTION_HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def query_recent_expenses() -> dict:
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    response = requests.post(url, headers=NOTION_HEADERS, json={"page_size": 10}, timeout=30)
    print("NOTION STATUS:", response.status_code)
    

    if not response.ok:
       raise Exception(f"Notion API error: {response.status_code} - {response.text}")
    return response.json()


def sum_recent_expenses() -> dict:
    data = query_recent_expenses()

    if not data:
        return {"total": 0.0, "items": []}

    results = data.get("results", [])

    total = 0.0
    items = []

    for row in results:
        props = row.get("properties", {})

        title_items = props.get("Title", {}).get("title", [])
        merchant = title_items[0]["plain_text"] if title_items else "Unknown"

        amount = props.get("Amount", {}).get("number") or 0

        category = props.get("Category", {}).get("select", {})
        category_name = (category.get("name") or "Unknown").title()

        date_prop = props.get("Date", {}).get("date", {})
        date_value = date_prop.get("start") if date_prop else None



        total += amount
        
        items.append({
            "merchant": merchant,
            "amount": amount,
            "category": category_name,
            "date": date_value
            
        })

    return {
        "total": total,
        "items": items
    }