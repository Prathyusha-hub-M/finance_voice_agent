from app.graph.builder import build_graph
from app.schemas.state import AgentState


def run_text_demo():
    app = build_graph()

    while True:
        user_text = input("\nYou: ").strip()
        if user_text.lower() in {"exit", "quit"}:
            break

        initial_state = AgentState(user_input=user_text)
        result = app.invoke(initial_state)

        print(f"Agent: {result['response']}")


if __name__ == "__main__":
    run_text_demo()