from app.schemas.state import AgentState
from app.services.llm import llm
from app.utils.logger import log_event


def analyze_spending_node(state: AgentState) -> AgentState:
    summary = state.summary_result
    log_event(state, "analyze", "generating insights")

    if not summary:
        state.response = "I couldn't find enough data to analyze your spending."
        state.execution_path.append("analyze_spending")
        return state

    prompt = f"""
You are a personal finance assistant.

Analyze the user's spending data and provide:
- key insights
- trends
- 1 to 2 actionable suggestions based on the spending
- motivate the user to spend less.

Keep it concise and conversational.

Data:
{summary}
"""

    result = llm.invoke(prompt)
    content = result.content

    if not isinstance(content, str):
        content = str(content)

    state.response = content.strip()
    state.execution_path.append("analyze_spending")

    return state