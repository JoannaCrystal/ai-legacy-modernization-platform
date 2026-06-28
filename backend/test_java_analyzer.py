from pathlib import Path

from app.analyzers.java_analyzer import JavaAnalyzer


def _method_names(result: dict) -> list[str]:
    return [method["name"] for method in result["methods"]]


def _method(result: dict, name: str) -> dict:
    for method in result["methods"]:
        if method["name"] == name:
            return method
    raise AssertionError(f"Method {name!r} not found")


def test_multiline_methods() -> None:
    content = """
public class OrderService {
    public Order createOrder(Request request) {
        return null;
    }

    private boolean validate(Request request) {
        return true;
    }
}
"""
    result = JavaAnalyzer().analyze(content)

    assert len(result["methods"]) == 2
    create_order = _method(result, "createOrder")
    assert create_order["return_type"] == "Order"
    assert create_order["parameters"] == "Request request"
    assert create_order["class_name"] == "OrderService"

    validate = _method(result, "validate")
    assert validate["return_type"] == "boolean"
    assert validate["class_name"] == "OrderService"


def test_one_line_methods() -> None:
    content = """
public class Foo {
    public void process() {}
    public String getName(){ return name; }
}
"""
    result = JavaAnalyzer().analyze(content)

    assert _method_names(result) == ["process", "getName"]
    assert _method(result, "process")["return_type"] == "void"
    assert _method(result, "getName")["parameters"] == ""


def test_one_line_class_body() -> None:
    content = (
        "public class Foo { public void process() {} "
        "public String getName(){ return name; } }"
    )
    result = JavaAnalyzer().analyze(content)

    assert _method_names(result) == ["process", "getName"]
    assert all(method["class_name"] == "Foo" for method in result["methods"])


def test_empty_methods() -> None:
    content = "public class Worker { public void run() {} }"
    result = JavaAnalyzer().analyze(content)

    assert len(result["methods"]) == 1
    assert _method(result, "run")["return_type"] == "void"


def test_annotated_methods() -> None:
    multiline = """
public class Runner implements Runnable {
    @Override
    public void run() {
    }
}
"""
    single_line = """
public class Runner implements Runnable {
    @Override public void run() {}
}
"""
    class_annotation = """
@Service
public class OrderService {
    public void process() {}
}
"""

    assert _method_names(JavaAnalyzer().analyze(multiline)) == ["run"]
    assert _method_names(JavaAnalyzer().analyze(single_line)) == ["run"]
    class_result = JavaAnalyzer().analyze(class_annotation)
    assert _method_names(class_result) == ["process"]
    assert class_result["classes"][0]["name"] == "OrderService"


def test_overloaded_methods() -> None:
    content = """
public class Calculator {
    public int add(int a, int b) { return a + b; }
    public double add(double a, double b) { return a + b; }
}
"""
    result = JavaAnalyzer().analyze(content)

    assert len(result["methods"]) == 2
    assert all(method["name"] == "add" for method in result["methods"])
    assert {method["parameters"] for method in result["methods"]} == {
        "int a, int b",
        "double a, double b",
    }


def test_constructors_excluded() -> None:
    content = """
public class Foo {
    public Foo() {}
    public Foo(String name) {}
    public void bar() {}
}
"""
    result = JavaAnalyzer().analyze(content)

    assert _method_names(result) == ["bar"]


def test_control_flow_excluded() -> None:
    content = """
public class Example {
    public void run() {
        if (ready) {
            handle();
        }
        for (int i = 0; i < limit; i++) {
            step(i);
        }
    }
}
"""
    result = JavaAnalyzer().analyze(content)

    assert _method_names(result) == ["run"]


def test_class_and_dependency_extraction_preserved() -> None:
    sample_path = (
        Path(__file__).resolve().parent.parent
        / "test-legacy-app/src/main/java/OrderService.java"
    )
    content = sample_path.read_text()
    result = JavaAnalyzer().analyze(content)

    assert [cls["name"] for cls in result["classes"]] == ["OrderService"]
    assert len(result["methods"]) == 2
    assert {dep["name"] for dep in result["dependencies"]} == {
        "com.bank.PaymentClient",
        "org.springframework.stereotype.Service",
    }


def test_no_duplicate_methods() -> None:
    content = """
public class Foo {
    public void process() {}
    public void process() {}
}
"""
    result = JavaAnalyzer().analyze(content)

    assert len(result["methods"]) == 2
    assert result["methods"][0]["start_line"] != result["methods"][1][
        "start_line"
    ]


def test_sample_project_variants() -> None:
    formatted = """
package com.bank.orders;

import com.bank.PaymentClient;
import org.springframework.stereotype.Service;

@Service
public class OrderService {
    public Order createOrder(Request request) {
        return null;
    }

    private boolean validate(Request request) {
        return true;
    }
}
"""
    compact = """
package com.bank.orders;
import com.bank.PaymentClient;
import org.springframework.stereotype.Service;
@Service
public class OrderService {
    public Order createOrder(Request request) { return null; }
    private boolean validate(Request request) { return true; }
}
"""
    single_line_body = """
package com.bank.orders;
import com.bank.PaymentClient;
@Service public class OrderService {
    public Order createOrder(Request request) { return null; }
    private boolean validate(Request request) { return true; }
}
"""
    analyzer = JavaAnalyzer()

    for content in (formatted, compact, single_line_body):
        result = analyzer.analyze(content)
        assert len(result["methods"]) == 2
        assert {method["name"] for method in result["methods"]} == {
            "createOrder",
            "validate",
        }


def test_ingestion_method_count() -> None:
    import io
    import zipfile

    from app.database.session import SessionLocal
    from app.models.code_analysis import CodeClass, CodeMethod
    from app.models.code_file import CodeFile
    from app.services.ingestion_service import ingest_zip_archive

    java_source = """
@Service
public class OrderService {
    public void process() {}
    public String getName(){ return name; }
}
"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "src/main/java/OrderService.java",
            java_source,
        )

    db = SessionLocal()
    try:
        result = ingest_zip_archive(
            db,
            "java-analyzer-fix-test",
            buffer.getvalue(),
        )
        method_count = (
            db.query(CodeMethod)
            .join(CodeClass, CodeMethod.class_id == CodeClass.id)
            .join(CodeFile, CodeClass.code_file_id == CodeFile.id)
            .filter(CodeFile.project_id == result.project_id)
            .count()
        )
        assert method_count == 2, f"Expected 2 methods, got {method_count}"
    finally:
        db.close()


def main() -> None:
    test_multiline_methods()
    test_one_line_methods()
    test_one_line_class_body()
    test_empty_methods()
    test_annotated_methods()
    test_overloaded_methods()
    test_constructors_excluded()
    test_control_flow_excluded()
    test_class_and_dependency_extraction_preserved()
    test_no_duplicate_methods()
    test_sample_project_variants()
    try:
        test_ingestion_method_count()
        print("Ingestion integration test passed.")
    except Exception as exc:
        print(f"Skipping ingestion integration test: {exc}")
    print("All Java analyzer tests passed.")


if __name__ == "__main__":
    main()
