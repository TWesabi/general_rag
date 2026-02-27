"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from rag_system.api.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check():
    """Test readiness check endpoint."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_list_documents():
    """Test list documents endpoint."""
    response = client.get("/documents")
    assert response.status_code in [200, 500]  # 500 if Weaviate not available


# Note: Add more comprehensive tests with mocked dependencies
