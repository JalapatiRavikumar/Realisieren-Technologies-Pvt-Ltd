"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_endpoint():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data
    assert "books" in data
    assert "quotes" in data
    assert "sources_detail" in data


def test_records_endpoint_pagination():
    response = client.get("/api/records?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert "total" in data
    assert len(data["records"]) <= 5


def test_records_endpoint_search():
    response = client.get("/api/records?search=Einstein")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for rec in data["records"]:
        combined = f"{rec.get('name_or_title', '')} {rec.get('author', '')} {rec.get('tags', '')} {rec.get('category', '')}".lower()
        assert "einstein" in combined


def test_records_endpoint_source_filter():
    response = client.get("/api/records?source=books")
    assert response.status_code == 200
    data = response.json()
    for rec in data["records"]:
        assert "book" in rec["source"].lower()


def test_download_csv_endpoint():
    response = client.get("/api/download/csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")


def test_download_summary_endpoint():
    response = client.get("/api/download/summary")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
