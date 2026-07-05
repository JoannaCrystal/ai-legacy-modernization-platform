import io
import os
import zipfile
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://admin:password@localhost:5432/modernizer_db",
)

from fastapi.testclient import TestClient

from app.core.config import settings, validate_startup_config
from app.core.exceptions import UploadValidationError
from app.core.upload_validation import validate_upload_filename, validate_zip_archive
from app.database.session import get_db
from app.main import app


client = TestClient(app, raise_server_exceptions=False)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == settings.APP_NAME
    assert payload["version"] == settings.APP_VERSION


def test_ready_endpoint_with_mock_db() -> None:
    mock_db = MagicMock()
    mock_db.execute.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_db

    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert len(payload["dependencies"]) == 2
    assert all(item["status"] == "healthy" for item in payload["dependencies"])


def test_ready_endpoint_reports_unhealthy_database() -> None:
    from sqlalchemy.exc import SQLAlchemyError

    mock_db = MagicMock()
    mock_db.execute.side_effect = SQLAlchemyError("connection refused")
    app.dependency_overrides[get_db] = lambda: mock_db

    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "not_ready"
    database = next(
        item for item in payload["dependencies"] if item["name"] == "database"
    )
    assert database["status"] == "unhealthy"


def _mock_db_with_no_project() -> MagicMock:
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    return mock_db


def test_global_exception_handler_project_not_found() -> None:
    app.dependency_overrides[get_db] = _mock_db_with_no_project

    try:
        response = client.get("/projects/999999/analysis")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    payload = response.json()
    assert payload["error_code"] == "PROJECT_NOT_FOUND"
    assert payload["message"] == "Project not found"
    assert payload["detail"] == payload["message"]
    assert payload["path"] == "/projects/999999/analysis"
    assert "timestamp" in payload


def test_global_exception_handler_validation_error() -> None:
    response = client.get("/knowledge/search")

    assert response.status_code == 422
    payload = response.json()
    assert payload["error_code"] == "VALIDATION_ERROR"
    assert payload["path"] == "/knowledge/search"


def test_upload_filename_validation() -> None:
    try:
        validate_upload_filename("legacy-app.tar.gz")
        raise AssertionError("Expected UploadValidationError")
    except UploadValidationError as exc:
        assert "ZIP" in exc.message


def test_upload_rejects_empty_zip() -> None:
    try:
        validate_zip_archive(b"")
        raise AssertionError("Expected UploadValidationError")
    except UploadValidationError as exc:
        assert "empty" in exc.message.lower()


def test_upload_rejects_unsupported_contents() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("readme.txt", "unsupported")

    try:
        validate_zip_archive(buffer.getvalue())
        raise AssertionError("Expected UploadValidationError")
    except UploadValidationError as exc:
        assert "supported source files" in exc.message.lower()


def test_upload_accepts_supported_java_file() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "src/main/java/Example.java",
            "public class Example {}",
        )

    validate_zip_archive(buffer.getvalue())


def test_upload_api_returns_structured_error() -> None:
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    try:
        response = client.post(
            "/projects/upload",
            data={"name": "Invalid Upload"},
            files={"file": ("legacy.txt", b"not-a-zip", "text/plain")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    payload = response.json()
    assert payload["error_code"] == "UPLOAD_VALIDATION_ERROR"
    assert payload["path"] == "/projects/upload"


def test_configuration_validation_requires_openai_key() -> None:
    original_key = settings.OPENAI_API_KEY
    settings.OPENAI_API_KEY = ""

    try:
        try:
            validate_startup_config()
            raise AssertionError("Expected RuntimeError")
        except RuntimeError as exc:
            assert "OPENAI_API_KEY" in str(exc)
    finally:
        settings.OPENAI_API_KEY = original_key


def test_configuration_validation_requires_database_url() -> None:
    original_url = settings.DATABASE_URL
    settings.DATABASE_URL = "   "

    try:
        try:
            validate_startup_config()
            raise AssertionError("Expected RuntimeError")
        except RuntimeError as exc:
            assert "DATABASE_URL" in str(exc)
    finally:
        settings.DATABASE_URL = original_url


def test_report_generation_failure() -> None:
    mock_db = MagicMock()
    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "Demo"
    mock_project.created_at = datetime(2026, 6, 27, tzinfo=timezone.utc)
    mock_snapshot = MagicMock()
    mock_snapshot.id = 10
    mock_snapshot.payload = {"risk_analysis": {"overall_risk": "LOW"}}
    mock_snapshot.overall_risk = "LOW"

    project_query = MagicMock()
    project_query.filter.return_value.first.return_value = mock_project
    snapshot_query = MagicMock()
    snapshot_query.filter.return_value.order_by.return_value.first.return_value = (
        mock_snapshot
    )
    mock_db.query.side_effect = [project_query, snapshot_query]
    app.dependency_overrides[get_db] = lambda: mock_db

    try:
        with patch(
            "app.services.report_service.generate_pdf",
            side_effect=RuntimeError("PDF rendering failed"),
        ):
            response = client.post("/projects/1/reports/generate")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    payload = response.json()
    assert payload["error_code"] == "INTERNAL_ERROR"
    assert payload["path"] == "/projects/1/reports/generate"


def main() -> None:
    test_health_endpoint()
    test_ready_endpoint_with_mock_db()
    test_ready_endpoint_reports_unhealthy_database()
    test_global_exception_handler_project_not_found()
    test_global_exception_handler_validation_error()
    test_upload_filename_validation()
    test_upload_rejects_empty_zip()
    test_upload_rejects_unsupported_contents()
    test_upload_accepts_supported_java_file()
    test_upload_api_returns_structured_error()
    test_configuration_validation_requires_openai_key()
    test_configuration_validation_requires_database_url()
    test_report_generation_failure()
    print("All production hardening tests passed.")


if __name__ == "__main__":
    main()
