import logging

from langgraph.graph import END, START, StateGraph

from app.agents.state import ModernizationState

logger = logging.getLogger(__name__)


def code_agent(state: ModernizationState) -> ModernizationState:
    logger.info("Executing code_agent")
    return state


def dependency_agent(state: ModernizationState) -> ModernizationState:
    logger.info("Executing dependency_agent")
    return state


def risk_agent(state: ModernizationState) -> ModernizationState:
    logger.info("Executing risk_agent")
    return state


def modernization_agent(state: ModernizationState) -> ModernizationState:
    logger.info("Executing modernization_agent")
    return state


def build_graph():
    graph = StateGraph(ModernizationState)

    graph.add_node("code_agent", code_agent)
    graph.add_node("dependency_agent", dependency_agent)
    graph.add_node("risk_agent", risk_agent)
    graph.add_node("modernization_agent", modernization_agent)

    graph.add_edge(START, "code_agent")
    graph.add_edge("code_agent", "dependency_agent")
    graph.add_edge("dependency_agent", "risk_agent")
    graph.add_edge("risk_agent", "modernization_agent")
    graph.add_edge("modernization_agent", END)

    return graph.compile()


graph = build_graph()
