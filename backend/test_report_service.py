from datetime import datetime, timezone

from app.services.pdf_service import generate_pdf
from app.services.report_builder_service import build_enterprise_report

SAMPLE_PAYLOAD = {
    "code_analysis": {
        "summary": "Application contains 3 classes and 5 methods",
        "detected_components": ["CustomerController"],
    },
    "dependency_analysis": {
        "total_dependencies": 2,
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
                "classes": ["CustomerController", "CustomerService"],
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
        "application_overview": "Legacy Spring monolith.",
        "architecture_summary": "Layered monolith architecture.",
        "components": [],
        "business_capabilities": [],
        "technology_summary": "Java, Spring, SOAP",
        "technical_risks": ["Legacy SOAP dependencies"],
        "modernization_opportunities": ["Replace SOAP with REST"],
    },
    "modernization_plan": {
        "architecture_assessment": "Monolith suitable for phased migration",
        "key_risks": ["SOAP dependency risk"],
        "recommended_steps": ["Introduce REST facade"],
        "target_architecture": "Cloud-native microservices",
    },
    "code_modernization": {
        "opportunities": [
            {
                "component": "Customer Management",
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
    "modernization_roadmap": {
        "phases": [
            {
                "phase": 1,
                "title": "Legacy Integration Modernization",
                "items": [
                    {
                        "component": "Customer Management",
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
            }
        ]
    },
    "dependencies": [
        {
            "dependency": "javax.xml.soap.SOAPConnection",
            "technology": "SOAP",
            "risk_level": "HIGH",
        }
    ],
}


def test_report_builder_includes_required_sections() -> None:
    report = build_enterprise_report(
        project_name="Demo Legacy App",
        project_id=1,
        upload_date=datetime(2026, 6, 27, tzinfo=timezone.utc),
        analysis_payload=SAMPLE_PAYLOAD,
    )

    assert report["cover_page"]["subtitle"] == "Demo Legacy App"
    assert report["executive_summary"]
    assert report["architecture_components"]
    assert report["business_capabilities"]
    assert report["modernization_plan"]
    assert report["code_modernization"]
    assert report["modernization_roadmap"]
    assert report["report_generated_at"]


def test_pdf_generation_produces_bytes() -> None:
    report = build_enterprise_report(
        project_name="Demo Legacy App",
        project_id=1,
        upload_date=datetime(2026, 6, 27, tzinfo=timezone.utc),
        analysis_payload=SAMPLE_PAYLOAD,
    )

    pdf_bytes = generate_pdf(report)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")


def main() -> None:
    test_report_builder_includes_required_sections()
    test_pdf_generation_produces_bytes()
    print("All enterprise reporting tests passed.")


if __name__ == "__main__":
    main()
