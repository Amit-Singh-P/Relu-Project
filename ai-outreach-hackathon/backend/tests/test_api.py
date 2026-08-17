from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_file = tmp_path / "results.json"
    monkeypatch.setattr(main, "store", main.ResultStore(data_file))
    return TestClient(main.app)


def _fake_profile(url: str, label: str = "") -> dict:
    return {
        "website_name": label or "Acme",
        "company_name": "Acme Inc.",
        "address": "123 Main St",
        "mobile_number": "+1-555-000-0000",
        "mail": ["hi@acme.com"],
        "core_service": "Widgets",
        "target_customer": "Enterprises",
        "probable_pain_point": "Manual processes",
        "outreach_opener": "Hi team...",
        "source_url": url,
        "label": label,
        "scraped_at": "2026-01-01T00:00:00+00:00",
        "status": "ok",
        "pages_scraped": [url],
    }


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_enrich_success_returns_full_schema(client):
    with patch.object(main, "enrich_company", side_effect=_fake_profile):
        response = client.post("/enrich", json={"url": "https://acme.com", "website_name": "Acme"})

    assert response.status_code == 200
    body = response.json()
    for key in ["website_name", "company_name", "address", "mobile_number", "mail",
                "core_service", "target_customer", "probable_pain_point", "outreach_opener"]:
        assert key in body


def test_enrich_rejects_blank_url(client):
    response = client.post("/enrich", json={"url": "   "})
    assert response.status_code == 422


def test_enrich_rejects_missing_url_field(client):
    response = client.post("/enrich", json={})
    assert response.status_code == 422


def test_enrich_persists_and_results_returns_it(client):
    with patch.object(main, "enrich_company", side_effect=_fake_profile):
        client.post("/enrich", json={"url": "https://acme.com", "website_name": "Acme"})

    response = client.get("/results")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["source_url"] == "https://acme.com"


def test_enrich_upserts_same_url_instead_of_duplicating(client):
    with patch.object(main, "enrich_company", side_effect=_fake_profile):
        client.post("/enrich", json={"url": "https://acme.com", "website_name": "Acme"})
        client.post("/enrich", json={"url": "https://acme.com", "website_name": "Acme v2"})

    results = client.get("/results").json()
    assert len(results) == 1
    assert results[0]["website_name"] == "Acme v2"


def test_enrich_unreachable_site_returns_schema_stable_empty_profile(client):
    def unreachable(url, label=""):
        return {
            "website_name": label,
            "company_name": "",
            "address": "",
            "mobile_number": "",
            "mail": [],
            "core_service": "",
            "target_customer": "",
            "probable_pain_point": "",
            "outreach_opener": "",
            "source_url": url,
            "label": label,
            "scraped_at": "2026-01-01T00:00:00+00:00",
            "status": "unreachable",
        }

    with patch.object(main, "enrich_company", side_effect=unreachable):
        response = client.post("/enrich", json={"url": "https://this-domain-does-not-exist-xyz123.com"})

    assert response.status_code == 200
    body = response.json()
    assert body["mail"] == []
    assert body["company_name"] == ""
    assert body["status"] == "unreachable"


def test_results_empty_by_default(client):
    response = client.get("/results")
    assert response.status_code == 200
    assert response.json() == []
