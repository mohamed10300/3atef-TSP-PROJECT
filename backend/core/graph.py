"""
LangGraph StateGraph pipeline wiring all agents in order:
  email_agent → excel_agent → event_agent → venue_agent →
  hotel_agent → pricing_agent → policy_agent →
  approval_node → scoring_node → reporting_agent
"""
from langgraph.graph import StateGraph, END

from backend.core.state import AgentState
from backend.agents.email_agent import email_agent
from backend.agents.excel_agent import excel_agent
from backend.agents.event_agent import event_agent
from backend.agents.venue_agent import venue_agent
from backend.agents.hotel_agent import hotel_agent
from backend.agents.pricing_agent import pricing_agent
from backend.agents.policy_agent import policy_agent
from backend.agents.reporting_agent import reporting_agent
from backend.core.approval_engine import run_approval
from backend.core.scoring_engine import calculate_scores
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def approval_node(state: AgentState) -> AgentState:
    hotels = state.get("hotels", [])
    result = run_approval(hotels)
    return {**state, "approval": result, "step": "approval_done"}


async def scoring_node(state: AgentState) -> AgentState:
    hotels = state.get("hotels", [])
    event = state.get("event") or {}
    event_type = event.get("type", "business")
    result = calculate_scores(hotels, event_type=event_type)
    return {**state, "scores": result, "step": "scoring_done"}


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("email_agent", email_agent)
    graph.add_node("excel_agent", excel_agent)
    graph.add_node("event_agent", event_agent)
    graph.add_node("venue_agent", venue_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("pricing_agent", pricing_agent)
    graph.add_node("policy_agent", policy_agent)
    graph.add_node("approval_node", approval_node)
    graph.add_node("scoring_node", scoring_node)
    graph.add_node("reporting_agent", reporting_agent)

    graph.set_entry_point("email_agent")

    graph.add_edge("email_agent", "excel_agent")
    graph.add_edge("excel_agent", "event_agent")
    graph.add_edge("event_agent", "venue_agent")
    graph.add_edge("venue_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "pricing_agent")
    graph.add_edge("pricing_agent", "policy_agent")
    graph.add_edge("policy_agent", "approval_node")
    graph.add_edge("approval_node", "scoring_node")
    graph.add_edge("scoring_node", "reporting_agent")
    graph.add_edge("reporting_agent", END)

    return graph


def compile_graph():
    return build_graph().compile()


async def run_pipeline(initial_state: AgentState) -> AgentState:
    app = compile_graph()
    final_state = await app.ainvoke(initial_state)
    return final_state


if __name__ == "__main__":
    import asyncio

    initial: AgentState = {
        "raw_event_input": "Arab Health 2025 — Dubai World Trade Centre, Jan 27-30, 2025",
        "excel_path": None,
        "email_content": None,
        "event": None,
        "hotels": [],
        "vendor_prices": {},
        "competitor_prices": {},
        "approval": None,
        "scores": None,
        "report": None,
        "error": None,
        "step": "start",
    }

    result = asyncio.run(run_pipeline(initial))
    print("Final step:", result.get("step"))
    print("Decision:", result.get("approval", {}).get("decision"))
    print("Score:", result.get("scores", {}).get("profitability_score"))
