from unittest.mock import MagicMock, patch

from app.agents.code_modernization_agent import CodeModernizationAgent
from app.agents.graph import build_graph
from app.agents.state import ModernizationState

SAMPLE_CODE_MODERNIZATION = {
    "opportunities": [
        {
            "component": "Customer Management",
            "legacy_technology_or_pattern": "SOAP service integration",
            "recommended_approach": "REST API",
            "justification": (
                "High-risk SOAP dependency detected in customer component."
            ),
            "implementation_strategy": (
                "Introduce a REST controller alongside the SOAP endpoint "
                "and migrate consumers incrementally."
            ),
            "example_modernized_code": (
                "@RestController\n"
                "@RequestMapping(\"/customers\")\n"
                "public class CustomerController {\n"
                "  @GetMapping(\"/{id}\")\n"
                "  public Customer getCustomer(@PathVariable Long id) {\n"
                "    return customerService.findById(id);\n"
                "  }\n"
                "}"
            ),
            "replaces": "Legacy SOAP CustomerService endpoint",
            "migration_considerations": [
                "Maintain backward compatibility during transition",
                "Update API consumers to use JSON payloads",
            ],
            "migration_risks": [
                "Temporary dual-protocol maintenance overhead",
            ],
            "enterprise_references": [
                "Use strangler fig pattern for SOAP to REST migration",
            ],
        }
    ]
}


def _base_state() -> ModernizationState:
    return {
        "project_id": 1,
        "classes": [{"name": "CustomerController"}],
        "methods": [{"name": "getCustomer", "class": "CustomerController"}],
        "dependencies": [
            {
                "dependency": "javax.xml.soap.SOAPConnection",
                "technology": "SOAP",
                "risk_level": "HIGH",
            }
        ],
        "code_analysis": {
            "summary": "1 class and 1 method",
            "detected_components": ["CustomerController"],
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
                    "name": "Customer Management",
                    "responsibility": "Handles customer operations",
                    "classes": ["CustomerController"],
                }
            ]
        },
        "business_capabilities": {
            "capabilities": [
                {
                    "name": "Customer Management",
                    "description": "Supports customer profile management.",
                }
            ]
        },
        "architecture_report": {
            "application_overview": "Legacy SOAP-enabled customer service.",
            "architecture_summary": "Layered monolith",
            "components": [],
            "business_capabilities": [],
            "technology_summary": "Java, SOAP",
            "technical_risks": ["Legacy SOAP dependencies"],
            "modernization_opportunities": ["Replace SOAP with REST"],
        },
        "modernization_plan": {
            "architecture_assessment": "Monolith with legacy SOAP integrations",
            "key_risks": ["SOAP dependency risk"],
            "recommended_steps": ["Modernize customer API layer"],
            "target_architecture": "Cloud-ready REST services",
        },
        "retrieved_context": [
            "Strangler fig pattern supports incremental SOAP migration.",
        ],
    }


def test_code_modernization_agent_stores_artifacts_in_state() -> None:
    agent = CodeModernizationAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_code_modernization.return_value = (
        SAMPLE_CODE_MODERNIZATION
    )

    result = agent.execute(_base_state())

    assert result["code_modernization"] == SAMPLE_CODE_MODERNIZATION
    agent.llm_service.generate_code_modernization.assert_called_once()

    call_context = (
        agent.llm_service.generate_code_modernization.call_args[0][0]
    )
    assert call_context["modernization_plan"]
    assert call_context["architecture_report"]
    assert call_context["retrieved_context"]


def test_code_modernization_agent_fallback_on_llm_failure() -> None:
    agent = CodeModernizationAgent()
    agent.llm_service = MagicMock()
    agent.llm_service.generate_code_modernization.side_effect = RuntimeError(
        "LLM unavailable"
    )

    result = agent.execute(_base_state())

    assert result["code_modernization"] == {"opportunities": []}


@patch("app.agents.knowledge_agent.KnowledgeRetriever")
def test_graph_runs_code_modernization_agent_after_modernization(
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

    code_modernization_llm = MagicMock()
    code_modernization_llm.generate_code_modernization.return_value = (
        SAMPLE_CODE_MODERNIZATION
    )
    graph_module.code_modernization_agent.llm_service = (
        code_modernization_llm
    )

    roadmap_llm = MagicMock()
    roadmap_llm.generate_modernization_roadmap.return_value = {"phases": []}
    graph_module.modernization_roadmap_agent.llm_service = roadmap_llm

    mock_retriever_cls.return_value.retrieve.return_value = []

    graph = build_graph()
    result = graph.invoke(_base_state())

    code_modernization_llm.generate_code_modernization.assert_called_once()
    assert result["code_modernization"] == SAMPLE_CODE_MODERNIZATION


def main() -> None:
    test_code_modernization_agent_stores_artifacts_in_state()
    test_code_modernization_agent_fallback_on_llm_failure()
    test_graph_runs_code_modernization_agent_after_modernization()
    print("All code modernization agent tests passed.")


if __name__ == "__main__":
    main()
