import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, Any, List
from collections import defaultdict

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def create_expense_page(expense: Dict[str, Any]) -> Dict[str, Any]:
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


def query_recent_expenses() -> Dict[str, Any]:
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

    response = requests.post(
        url,
        headers=NOTION_HEADERS,
        json={"page_size": 20,
              "sorts": [
            {
                "property": "Date",
                "direction": "descending"
            }
        ]
        },  
        timeout=30
    )

    if not response.ok:
        raise Exception(f"Notion API error: {response.status_code} - {response.text}")

    return response.json()



def sum_recent_expenses() -> Dict[str, Any]:
    data = query_recent_expenses()

    if not data:
        return {"total": 0.0, "items": []}

    results = data.get("results", [])

    total = 0.0
    items: List[Dict[str, Any]] = []

    for row in results:
        props = row.get("properties", {})

        title_items = props.get("Title", {}).get("title", [])
        merchant = title_items[0]["plain_text"] if title_items else "Unknown"

        amount = props.get("Amount", {}).get("number") or 0.0

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



def get_dashboard_summary() -> Dict[str, Any]:
    data = query_recent_expenses()

    # default safe response
    result: Dict[str, Any] = {
        "total_spend": 0.0,
        "weekly_spend": 0.0,
        "top_category": "None",
        "category_breakdown": {},
        "expenses": []
    }

    if not data:
        return result

    results = data.get("results", [])

    category_totals: Dict[str, float] = defaultdict(float)

    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    for row in results:
        props = row.get("properties", {})

        # Merchant
        title_items = props.get("Title", {}).get("title", [])
        merchant = title_items[0]["plain_text"] if title_items else "Unknown"

        # Amount
        amount = props.get("Amount", {}).get("number") or 0.0

        # Category
        category = props.get("Category", {}).get("select")

        category_name = (
            (category.get("name") if category else "Other")
        ).title()

        # Date
        date_prop = props.get("Date", {}).get("date", {})
        date_str = date_prop.get("start") if date_prop else None

        date_obj = None
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str).date()
            except ValueError:
                date_obj = None

        # Aggregations
        result["total_spend"] += amount
        category_totals[category_name] += amount

        if date_obj and date_obj >= week_ago:
            result["weekly_spend"] += amount

        # Store item
        result["expenses"].append({
            "merchant": merchant,
            "amount": amount,
            "category": category_name,
            "date": date_str
        })


    if category_totals:
        result["top_category"] = max(category_totals.items(), key=lambda x: x[1])[0]

    result["category_breakdown"] = dict(category_totals)

    return result