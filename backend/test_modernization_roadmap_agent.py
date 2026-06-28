from unittest.mock import MagicMock, patch

from app.agents.graph import build_graph
from app.agents.modernization_roadmap_agent import ModernizationRoadmapAgent
from app.agents.state import ModernizationState

SAMPLE_ROADMAP = {
    "phases": [
        {
            "phase": 1,
            "title": "Legacy Integration Modernization",
            "items": [
                {
                    "component": "Customer Integration",
                    "business_capability": "Customer Management",
                    "technical_risk": "High",
                    "priority": "High",
                    "business_impact": "High",
                    "implementation_complexity": "Medium",
                    "recommended_action": (
                        "Introduce REST facade for SOAP integration"
                    ),
                    "dependencies": [],
                    "expected_outcome": "Reduce legacy integration risk",
                }
            ],
        },
        {
            "phase": 2,
            "title": "Service Modernization",
            "items": [
                {
                    "component": "Payment Service",
                    "business_capability": "Payment Processing",
                    "technical_risk": "Medium",
                    "priority": "High",
                    "business_impact": "High",
                    "implementation_complexity": "High",
                    "recommended_action": (
                        "Migrate Payment Service to Spring Boot"
                    ),
                    "dependencies": ["Phase 1 REST facade"],
                    "expected_outcome": (
                        "Cloud-ready payment processing service"
                    ),
                }
            ],
        },
    ]
}


def _base_state() -> ModernizationState:
    return {
        "project_id": 1,
        "classes": [{"name": "PaymentService"}],
        "methods": [{"name": "processPayment", "class": "PaymentService"}],
        "dependencies": [
            {
                "dependency": "javax.xml.soap.SOAPConnection",
                "technology": "SOAP",
                "risk_level": "HIGH",
            }
        ],
        "code_analysis": {
            "summary": "1 class and 1 method",
            "detected_components": ["PaymentService"],
        },
        "dependency_analysis": {
            "total_dependencies": 1,
            "high_risk_dependencies": [
                {
                    "dependency": "javax.xml.soap.SOAPConnection",
                    "technology": "SOAP",
                    "risk_level": "HIGH",
                }
            ],
        },
        "risk_analysis": {
            "overall_risk": "HIGH",
            "reason": "Found 1 high-risk dependency requiring attention",
        },
        "architecture_summary": {
            "components": [
                {
                    "name": "Payment Service",
                    "responsibility": "Processes payments",
                    "classes": ["PaymentService"],
                }
            ]
        },
        "business_capabilities": {
            "capabilities": [
                {
                    "name": "Payment Processing",
                    "description": "Handles customer payment transactions.",
                }
            ]
        },
        "architecture_report": {
            "application_overview": "Legacy payment monolith.",
            "architecture_summary": "Layered monolith",
            "components": [],
            "business_capabilities": [],
            "technology_summary": "Java, SOAP",
            "technical_risks": ["Legacy SOAP dependencies"],
            "modernization_opportunities": ["Replace SOAP with REST"],
        },
        "modernization_plan": {
            "architecture_assessment": "Monolith with legacy integrations",
            "key_risks": ["SOAP dependency risk"],
            "recommended_steps": ["Modernize integration layer first"],
            "target_architecture": "Cloud-native microservices",
        },
        "code_modernization": {
            "opportunities": [
                {
                    "component": "Payment Service",
                    "legacy_technology_or_pattern": "SOAP Service",
                    "recommended_approach": "REST Controller",
                    "justification": "REST is cloud-native.",
                    "implementation_strategy": "Introduce REST facade.",
                    "example_modernized_code": "@RestController",
                    "replaces": "SOAP endpoint",
                    "migration_considerations": [],
                    "migration_risks": [],
                    "enterprise_references": [],
                }
            ]
        },
        "retrieved_context": [
            "Strangler fig pattern supports incremental migration.",
        ],
    }


def test_modernization_roadmap_agent_stores_roadmap_in_state() -> None:
    agent = ModernizationRoadmapAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_modernization_roadmap.return_value = (
        SAMPLE_ROADMAP
    )

    result = agent.execute(_base_state())

    assert result["modernization_roadmap"] == SAMPLE_ROADMAP
    agent.llm_service.generate_modernization_roadmap.assert_called_once()

    call_context = (
        agent.llm_service.generate_modernization_roadmap.call_args[0][0]
    )
    assert call_context["code_modernization"]
    assert call_context["modernization_plan"]
    assert call_context["retrieved_context"]


def test_modernization_roadmap_agent_fallback_on_llm_failure() -> None:
    agent = ModernizationRoadmapAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_modernization_roadmap.side_effect = RuntimeError(
        "LLM unavailable"
    )

    result = agent.execute(_base_state())

    assert result["modernization_roadmap"] == {"phases": []}


@patch("app.agents.knowledge_agent.KnowledgeRetriever")
def test_graph_runs_roadmap_agent_after_code_modernization(
    mock_retriever_cls: MagicMock,
) -> None:
    from app.agents import graph as graph_module

    graph_module.architecture_agent.llm_service = MagicMock()
    graph_module.architecture_agent.llm_service.generate_architecture_summary.return_value = {  # noqa: E501
        "components": []
    }

    graph_module.business_capability_agent.llm_service = MagicMock()
    graph_module.business_capability_agent.llm_service.generate_business_capabilities.return_value = {  # noqa: E501
        "capabilities": []
    }

    graph_module.documentation_agent.llm_service = MagicMock()
    graph_module.documentation_agent.llm_service.generate_architecture_report.return_value = {  # noqa: E501
        "application_overview": "",
        "architecture_summary": "",
        "components": [],
        "business_capabilities": [],
        "technology_summary": "",
        "technical_risks": [],
        "modernization_opportunities": [],
    }

    graph_module.modernization_agent.llm_service = MagicMock()
    graph_module.modernization_agent.llm_service.generate_modernization_strategy.return_value = {  # noqa: E501
        "architecture_assessment": "",
        "key_risks": [],
        "recommended_steps": [],
        "target_architecture": "",
    }

    graph_module.code_modernization_agent.llm_service = MagicMock()
    graph_module.code_modernization_agent.llm_service.generate_code_modernization.return_value = {  # noqa: E501
        "opportunities": []
    }

    roadmap_llm = MagicMock()
    roadmap_llm.generate_modernization_roadmap.return_value = SAMPLE_ROADMAP
    graph_module.modernization_roadmap_agent.llm_service = roadmap_llm

    mock_retriever_cls.return_value.retrieve.return_value = []

    graph = build_graph()
    result = graph.invoke(_base_state())

    roadmap_llm.generate_modernization_roadmap.assert_called_once()
    assert result["modernization_roadmap"] == SAMPLE_ROADMAP


def main() -> None:
    test_modernization_roadmap_agent_stores_roadmap_in_state()
    test_modernization_roadmap_agent_fallback_on_llm_failure()
    test_graph_runs_roadmap_agent_after_code_modernization()
    print("All modernization roadmap agent tests passed.")


if __name__ == "__main__":
    main()
