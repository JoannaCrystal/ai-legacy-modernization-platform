from app.services.dependency_intelligence_service import (
    DependencyIntelligenceService,
)


def main() -> None:
    service = DependencyIntelligenceService()

    test_cases = [
        ("javax.xml.soap.SOAPMessage", "HIGH", "SOAP"),
        ("org.springframework.stereotype.Service", "LOW", "Spring Framework"),
        ("org.apache.log4j.Logger", "HIGH", "Log4j"),
    ]

    for dependency_name, expected_risk, expected_technology in test_cases:
        result = service.analyze_dependency(dependency_name)
        assert result["risk_level"] == expected_risk, (
            f"Expected {expected_risk} for {dependency_name}, "
            f"got {result['risk_level']}"
        )
        assert result["technology"] == expected_technology, (
            f"Expected {expected_technology} for {dependency_name}, "
            f"got {result['technology']}"
        )
        print(result)

    print("All dependency intelligence tests passed.")


if __name__ == "__main__":
    main()
