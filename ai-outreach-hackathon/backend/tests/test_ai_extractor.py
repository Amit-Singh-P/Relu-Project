from unittest.mock import patch

from app.pipeline import ai_extractor
from app.pipeline.ai_extractor import _parse_json_response, _verify_against_source, extract_profile


def test_parse_json_response_handles_plain_json():
    assert _parse_json_response('{"company_name": "Acme"}') == {"company_name": "Acme"}


def test_parse_json_response_strips_markdown_fences():
    raw = '```json\n{"company_name": "Acme"}\n```'
    assert _parse_json_response(raw) == {"company_name": "Acme"}


def test_parse_json_response_extracts_json_from_surrounding_prose():
    raw = 'Here is the result:\n{"company_name": "Acme"}\nHope that helps!'
    assert _parse_json_response(raw) == {"company_name": "Acme"}


def test_parse_json_response_returns_empty_dict_on_garbage():
    assert _parse_json_response("not json at all") == {}


def test_verify_against_source_drops_hallucinated_email():
    profile = {"mail": ["fake@nowhere.com"], "mobile_number": ""}
    source = "Contact us at real@acme.com for more info."
    verified = _verify_against_source(profile, source)
    assert verified["mail"] == ["real@acme.com"]


def test_verify_against_source_keeps_email_present_in_source():
    profile = {"mail": ["real@acme.com"], "mobile_number": ""}
    source = "Reach us at real@acme.com anytime."
    verified = _verify_against_source(profile, source)
    assert verified["mail"] == ["real@acme.com"]


def test_verify_against_source_drops_hallucinated_phone_number():
    profile = {"mail": [], "mobile_number": "+1-555-999-0000"}
    source = "Call our office at +1 (555) 123-4567 for support."
    verified = _verify_against_source(profile, source)
    assert verified["mobile_number"] == ""


def test_verify_against_source_keeps_phone_number_present_in_source_regardless_of_formatting():
    profile = {"mail": [], "mobile_number": "555 123 4567"}
    source = "Call our office at +1 (555) 123-4567 for support."
    verified = _verify_against_source(profile, source)
    assert verified["mobile_number"] == "555 123 4567"


def test_extract_profile_returns_empty_profile_for_blank_context():
    profile = extract_profile("   ", "https://acme.com")
    assert profile["mail"] == []
    assert profile["company_name"] == ""


def test_extract_profile_returns_empty_profile_when_llm_raises():
    import anthropic
    import httpx

    dummy_request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    with patch.object(
        ai_extractor,
        "call_llm",
        side_effect=anthropic.APIError("boom", request=dummy_request, body=None),
    ):
        profile = extract_profile("Some real content about Acme Corp.", "https://acme.com")
    assert profile["company_name"] == ""


def test_extract_profile_coerces_and_verifies_valid_llm_response():
    fake_response = '{"company_name": "Acme", "mail": ["hi@acme.com"], "mobile_number": ""}'
    with patch.object(ai_extractor, "call_llm", return_value=fake_response):
        profile = extract_profile("Contact hi@acme.com for Acme services.", "https://acme.com")
    assert profile["company_name"] == "Acme"
    assert profile["mail"] == ["hi@acme.com"]
