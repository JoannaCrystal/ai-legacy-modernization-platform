from unittest.mock import MagicMock, patch

from app.agents.architecture_agent import ArchitectureUnderstandingAgent
from app.agents.code_agent import CodeAnalyzerAgent
from app.agents.dependency_agent import DependencyAgent
from app.agents.graph import build_graph
from app.agents.modernization_agent import ModernizationAgent
from app.agents.risk_agent import RiskAgent
from app.agents.state import ModernizationState


SAMPLE_ARCHITECTURE = {
    "components": [
        {
            "name": "Customer Management",
            "responsibility": "Handles customer CRUD operations",
            "classes": [
                "CustomerController",
                "CustomerService",
                "CustomerRepository",
            ],
        },
        {
            "name": "Order Processing",
            "responsibility": "Processes customer orders",
            "classes": [
                "OrderController",
                "OrderService",
                "OrderRepository",
            ],
        },
    ]
}

SAMPLE_MODERNIZATION = {
    "architecture_assessment": (
        "Layered monolith suitable for incremental migration"
    ),
    "key_risks": ["Legacy SOAP dependencies"],
    "recommended_steps": ["Extract customer domain service"],
    "target_architecture": "Cloud-native microservices",
}


def _base_state() -> ModernizationState:
    return {
        "project_id": 1,
        "classes": [
            {
                "name": "CustomerController",
                "file": "CustomerController.java",
                "package": "com.example.customer",
            },
            {
                "name": "CustomerService",
                "file": "CustomerService.java",
                "package": "com.example.customer",
            },
            {
                "name": "OrderController",
                "file": "OrderController.java",
                "package": "com.example.order",
            },
        ],
        "methods": [
            {"name": "getCustomer", "class": "CustomerController"},
            {"name": "createOrder", "class": "OrderController"},
        ],
        "dependencies": [
            {
                "dependency": "org.springframework.stereotype.Service",
                "technology": "Spring Framework",
                "risk_level": "LOW",
            }
        ],
    }


def test_architecture_agent_stores_summary_in_state() -> None:
    agent = ArchitectureUnderstandingAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_architecture_summary.return_value = (
        SAMPLE_ARCHITECTURE
    )

    state = _base_state()
    CodeAnalyzerAgent().execute(state)
    DependencyAgent().execute(state)
    RiskAgent().execute(state)

    result = agent.execute(state)

    assert result["architecture_summary"] == SAMPLE_ARCHITECTURE
    agent.llm_service.generate_architecture_summary.assert_called_once()

    call_context = (
        agent.llm_service.generate_architecture_summary.call_args[0][0]
    )
    assert "code_analysis" in call_context
    assert "dependency_analysis" in call_context
    assert "risk_analysis" in call_context
    assert call_context["classes"]
    assert call_context["methods"]
    assert call_context["dependencies"]


def test_architecture_agent_fallback_on_llm_failure() -> None:
    agent = ArchitectureUnderstandingAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_architecture_summary.side_effect = (
        RuntimeError("LLM unavailable")
    )

    state = _base_state()
    CodeAnalyzerAgent().execute(state)
    DependencyAgent().execute(state)
    RiskAgent().execute(state)

    result = agent.execute(state)

    assert result["architecture_summary"] == {"components": []}


def test_modernization_agent_receives_architecture_summary() -> None:
    agent = ModernizationAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_modernization_strategy.return_value = (
        SAMPLE_MODERNIZATION
    )

    state = _base_state()
    state["code_analysis"] = {
        "summary": "3 classes",
        "detected_components": [],
    }
    state["dependency_analysis"] = {
        "total_dependencies": 1,
        "high_risk_dependencies": [],
    }
    state["risk_analysis"] = {
        "overall_risk": "LOW",
        "reason": "No high-risk deps",
    }
    state["architecture_summary"] = SAMPLE_ARCHITECTURE
    state["retrieved_context"] = ["Use strangler fig pattern for migration"]

    agent.execute(state)

    call_context = (
        agent.llm_service.generate_modernization_strategy.call_args[0][0]
    )
    assert call_context["architecture_summary"] == SAMPLE_ARCHITECTURE
    assert call_context["code_analysis"]
    assert call_context["dependency_analysis"]
    assert call_context["risk_analysis"]
    assert call_context["retrieved_context"]


@patch("app.agents.knowledge_agent.KnowledgeRetriever")
def test_graph_runs_architecture_agent_before_knowledge_and_modernization(
    mock_retriever_cls: MagicMock,
) -> None:
    from app.agents import graph as graph_module

    architecture_llm = MagicMock()
    architecture_llm.generate_architecture_summary.return_value = (
        SAMPLE_ARCHITECTURE
    )
    graph_module.architecture_agent.llm_service = architecture_llm

    business_llm = MagicMock()
    business_llm.generate_business_capabilities.return_value = {
        "capabilities": []
    }
    graph_module.business_capability_agent.llm_service = business_llm

    documentation_llm = MagicMock()
    documentation_llm.generate_architecture_report.return_value = {
        "application_overview": "",
        "architecture_summary": "",
        "components": [],
        "business_capabilities": [],
        "technology_summary": "",
        "technical_risks": [],
        "modernization_opportunities": [],
    }
    graph_module.documentation_agent.llm_service = documentation_llm

    modernization_llm = MagicMock()
    modernization_llm.generate_modernization_strategy.return_value = (
        SAMPLE_MODERNIZATION
    )
    graph_module.modernization_agent.llm_service = modernization_llm

    code_modernization_llm = MagicMock()
    code_modernization_llm.generate_code_modernization.return_value = {
        "opportunities": []
    }
    graph_module.code_modernization_agent.llm_service = (
        code_modernization_llm
    )

    mock_retriever_cls.return_value.retrieve.return_value = []

    graph = build_graph()
    state = _base_state()
    result = graph.invoke(state)

    architecture_llm.generate_architecture_summary.assert_called_once()
    modernization_llm.generate_modernization_strategy.assert_called_once()

    modernization_context = (
        modernization_llm.generate_modernization_strategy.call_args[0][0]
    )
    assert modernization_context["architecture_summary"] == SAMPLE_ARCHITECTURE
    assert result["architecture_summary"] == SAMPLE_ARCHITECTURE
    assert result["modernization_plan"] == SAMPLE_MODERNIZATION


def main() -> None:
    test_architecture_agent_stores_summary_in_state()
    test_architecture_agent_fallback_on_llm_failure()
    test_modernization_agent_receives_architecture_summary()
    test_graph_runs_architecture_agent_before_knowledge_and_modernization()
    print("All architecture understanding agent tests passed.")


if __name__ == "__main__":
    main()
