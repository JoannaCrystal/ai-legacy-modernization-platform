from unittest.mock import MagicMock, patch

from app.agents.business_capability_agent import BusinessCapabilityAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.graph import build_graph
from app.agents.modernization_agent import ModernizationAgent
from app.agents.state import ModernizationState

SAMPLE_ARCHITECTURE = {
    "components": [
        {
            "name": "Customer Management",
            "responsibility": "Handles customer CRUD operations",
            "classes": ["CustomerController", "CustomerService"],
        },
    ]
}

SAMPLE_BUSINESS_CAPABILITIES = {
    "capabilities": [
        {
            "name": "Customer Management",
            "description": (
                "Supports customer registration and profile management."
            ),
        },
        {
            "name": "Order Management",
            "description": "Handles order creation and fulfillment.",
        },
    ]
}

SAMPLE_ARCHITECTURE_REPORT = {
    "application_overview": "Legacy Spring monolith for customer orders.",
    "architecture_summary": "Layered architecture with domain components.",
    "components": [
        {
            "name": "Customer Management",
            "responsibility": "Customer CRUD",
        }
    ],
    "business_capabilities": [
        {
            "name": "Customer Management",
            "description": "Supports customer registration.",
        }
    ],
    "technology_summary": "Java, Spring Framework",
    "technical_risks": ["Legacy dependency versions"],
    "modernization_opportunities": ["Extract customer microservice"],
}

SAMPLE_MODERNIZATION = {
    "architecture_assessment": "Layered monolith suitable for migration",
    "key_risks": ["Legacy SOAP dependencies"],
    "recommended_steps": ["Extract customer domain service"],
    "target_architecture": "Cloud-native microservices",
}


def _base_state() -> ModernizationState:
    return {
        "project_id": 1,
        "classes": [{"name": "CustomerController"}],
        "methods": [{"name": "getCustomer", "class": "CustomerController"}],
        "dependencies": [
            {
                "dependency": "org.springframework.stereotype.Service",
                "technology": "Spring Framework",
                "risk_level": "LOW",
            }
        ],
        "code_analysis": {
            "summary": "1 class and 1 method",
            "detected_components": ["CustomerController"],
        },
        "dependency_analysis": {
            "total_dependencies": 1,
            "high_risk_dependencies": [],
        },
        "risk_analysis": {
            "overall_risk": "LOW",
            "reason": "No high-risk dependencies detected",
        },
        "architecture_summary": SAMPLE_ARCHITECTURE,
    }


def test_business_capability_agent_stores_capabilities_in_state() -> None:
    agent = BusinessCapabilityAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_business_capabilities.return_value = (
        SAMPLE_BUSINESS_CAPABILITIES
    )

    result = agent.execute(_base_state())

    assert result["business_capabilities"] == SAMPLE_BUSINESS_CAPABILITIES
    agent.llm_service.generate_business_capabilities.assert_called_once()

    call_context = (
        agent.llm_service.generate_business_capabilities.call_args[0][0]
    )
    assert call_context["architecture_summary"] == SAMPLE_ARCHITECTURE
    assert call_context["code_analysis"]
    assert call_context["dependency_analysis"]


def test_business_capability_agent_fallback_on_llm_failure() -> None:
    agent = BusinessCapabilityAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_business_capabilities.side_effect = (
        RuntimeError("LLM unavailable")
    )

    result = agent.execute(_base_state())

    assert result["business_capabilities"] == {"capabilities": []}


def test_documentation_agent_stores_report_in_state() -> None:
    agent = DocumentationAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_architecture_report.return_value = (
        SAMPLE_ARCHITECTURE_REPORT
    )

    state = _base_state()
    state["business_capabilities"] = SAMPLE_BUSINESS_CAPABILITIES
    state["retrieved_context"] = ["Use domain-driven design for extraction"]

    result = agent.execute(state)

    assert result["architecture_report"] == SAMPLE_ARCHITECTURE_REPORT
    agent.llm_service.generate_architecture_report.assert_called_once()

    call_context = (
        agent.llm_service.generate_architecture_report.call_args[0][0]
    )
    assert call_context["architecture_summary"] == SAMPLE_ARCHITECTURE
    assert call_context["business_capabilities"] == (
        SAMPLE_BUSINESS_CAPABILITIES
    )
    assert call_context["retrieved_context"]


def test_documentation_agent_fallback_on_llm_failure() -> None:
    agent = DocumentationAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_architecture_report.side_effect = RuntimeError(
        "LLM unavailable"
    )

    result = agent.execute(_base_state())

    assert result["architecture_report"]["application_overview"] == (
        "Documentation unavailable"
    )
    assert result["architecture_report"]["components"] == []


def test_modernization_agent_receives_new_state_fields() -> None:
    agent = ModernizationAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_modernization_strategy.return_value = (
        SAMPLE_MODERNIZATION
    )

    state = _base_state()
    state["business_capabilities"] = SAMPLE_BUSINESS_CAPABILITIES
    state["architecture_report"] = SAMPLE_ARCHITECTURE_REPORT
    state["retrieved_context"] = ["Enterprise migration guidance"]

    agent.execute(state)

    call_context = (
        agent.llm_service.generate_modernization_strategy.call_args[0][0]
    )
    assert call_context["business_capabilities"] == (
        SAMPLE_BUSINESS_CAPABILITIES
    )
    assert call_context["architecture_report"] == SAMPLE_ARCHITECTURE_REPORT
    assert call_context["architecture_summary"] == SAMPLE_ARCHITECTURE


@patch("app.agents.knowledge_agent.KnowledgeRetriever")
def test_graph_runs_new_agents_and_stores_outputs(
    mock_retriever_cls: MagicMock,
) -> None:
    from app.agents import graph as graph_module

    architecture_llm = MagicMock()
    architecture_llm.generate_architecture_summary.return_value = (
        SAMPLE_ARCHITECTURE
    )
    graph_module.architecture_agent.llm_service = architecture_llm

    business_llm = MagicMock()
    business_llm.generate_business_capabilities.return_value = (
        SAMPLE_BUSINESS_CAPABILITIES
    )
    graph_module.business_capability_agent.llm_service = business_llm

    documentation_llm = MagicMock()
    documentation_llm.generate_architecture_report.return_value = (
        SAMPLE_ARCHITECTURE_REPORT
    )
    graph_module.documentation_agent.llm_service = documentation_llm

    modernization_llm = MagicMock()
    modernization_llm.generate_modernization_strategy.return_value = (
        SAMPLE_MODERNIZATION
    )
    graph_module.modernization_agent.llm_service = modernization_llm

    mock_retriever_cls.return_value.retrieve.return_value = []

    graph = build_graph()
    result = graph.invoke(_base_state())

    architecture_llm.generate_architecture_summary.assert_called_once()
    business_llm.generate_business_capabilities.assert_called_once()
    documentation_llm.generate_architecture_report.assert_called_once()
    modernization_llm.generate_modernization_strategy.assert_called_once()

    modernization_context = (
        modernization_llm.generate_modernization_strategy.call_args[0][0]
    )
    assert result["business_capabilities"] == SAMPLE_BUSINESS_CAPABILITIES
    assert result["architecture_report"] == SAMPLE_ARCHITECTURE_REPORT
    assert modernization_context["business_capabilities"] == (
        SAMPLE_BUSINESS_CAPABILITIES
    )
    assert modernization_context["architecture_report"] == (
        SAMPLE_ARCHITECTURE_REPORT
    )


def main() -> None:
    test_business_capability_agent_stores_capabilities_in_state()
    test_business_capability_agent_fallback_on_llm_failure()
    test_documentation_agent_stores_report_in_state()
    test_documentation_agent_fallback_on_llm_failure()
    test_modernization_agent_receives_new_state_fields()
    test_graph_runs_new_agents_and_stores_outputs()
    print("All business capability and documentation agent tests passed.")


if __name__ == "__main__":
    main()
