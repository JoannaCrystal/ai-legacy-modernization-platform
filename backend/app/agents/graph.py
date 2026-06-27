from langgraph.graph import END, START, StateGraph

from app.agents.architecture_agent import ArchitectureUnderstandingAgent
from app.agents.business_capability_agent import BusinessCapabilityAgent
from app.agents.code_agent import CodeAnalyzerAgent
from app.agents.dependency_agent import DependencyAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.modernization_agent import ModernizationAgent
from app.agents.risk_agent import RiskAgent
from app.agents.state import ModernizationState

code_agent = CodeAnalyzerAgent()
dependency_agent = DependencyAgent()
risk_agent = RiskAgent()
architecture_agent = ArchitectureUnderstandingAgent()
business_capability_agent = BusinessCapabilityAgent()
knowledge_agent = KnowledgeAgent()
documentation_agent = DocumentationAgent()
modernization_agent = ModernizationAgent()


def build_graph():
    graph = StateGraph(ModernizationState)

    graph.add_node("code_agent", code_agent.execute)
    graph.add_node("dependency_agent", dependency_agent.execute)
    graph.add_node("risk_agent", risk_agent.execute)
    graph.add_node(
        "architecture_agent",
        architecture_agent.execute,
    )
    graph.add_node(
        "business_capability_agent",
        business_capability_agent.execute,
    )
    graph.add_node("knowledge_agent", knowledge_agent.execute)
    graph.add_node("documentation_agent", documentation_agent.execute)
    graph.add_node("modernization_agent", modernization_agent.execute)

    graph.add_edge(START, "code_agent")
    graph.add_edge("code_agent", "dependency_agent")
    graph.add_edge("dependency_agent", "risk_agent")
    graph.add_edge("risk_agent", "architecture_agent")
    graph.add_edge("architecture_agent", "business_capability_agent")
    graph.add_edge("business_capability_agent", "knowledge_agent")
    graph.add_edge("knowledge_agent", "documentation_agent")
    graph.add_edge("documentation_agent", "modernization_agent")
    graph.add_edge("modernization_agent", END)

    return graph.compile()


graph = build_graph()
