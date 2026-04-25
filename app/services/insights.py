from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_insight(summary: dict) -> str:
    prompt = f"""
    You are a financial assistant.

    Analyze the following spending data and give a short, clear summary (2-3 sentences max):

    Total Spend: {summary['total_spend']}
    Weekly Spend: {summary['weekly_spend']}
    Top Category: {summary['top_category']}
    Category Breakdown: {summary['category_breakdown']}

    Keep it simple and useful.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )


    content = response.choices[0].message.content

    return (content or "").strip()