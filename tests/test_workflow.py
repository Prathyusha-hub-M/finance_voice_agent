from app.graph.builder import build_graph
from app.schemas.state import AgentState


def test_log_expense_flow():
    graph = build_graph()

    state = AgentState(user_input="I spent 20 dollars on lunch")

    result = graph.invoke(state)

    assert result["intent"] == "log_expense"
    assert result["response"] is not None
    assert "validate" in result["execution_path"]


def test_summary_flow():
    graph = build_graph()

    state = AgentState(user_input="How much did I spend?")

    result = graph.invoke(state)

    assert result["intent"] == "summary_query"
    assert result["response"] is not None


def test_analyze_flow():
    graph = build_graph()

    state = AgentState(user_input="Analyze my spending")

    result = graph.invoke(state)

    assert result["intent"] == "analyze_spending"
    assert result["response"] is not None