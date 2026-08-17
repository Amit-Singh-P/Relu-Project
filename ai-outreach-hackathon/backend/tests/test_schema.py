from app.pipeline.schema import coerce_profile, empty_profile


def test_empty_profile_has_all_keys_with_safe_defaults():
    profile = empty_profile()
    assert profile["mail"] == []
    assert profile["company_name"] == ""
    assert set(profile.keys()) == {
        "website_name", "company_name", "address", "mobile_number", "mail",
        "core_service", "target_customer", "probable_pain_point", "outreach_opener",
    }


def test_coerce_profile_fills_missing_fields():
    partial = {"company_name": "Acme Inc.", "mail": "hi@acme.com"}
    profile = coerce_profile(partial)
    assert profile["company_name"] == "Acme Inc."
    assert profile["mail"] == ["hi@acme.com"]
    assert profile["address"] == ""


def test_coerce_profile_handles_non_dict_input():
    assert coerce_profile(None) == empty_profile()
    assert coerce_profile("not json") == empty_profile()
    assert coerce_profile([1, 2, 3]) == empty_profile()


def test_coerce_profile_drops_unknown_keys_and_normalizes_mail_list():
    raw = {
        "company_name": "Acme",
        "mail": ["a@acme.com", "", "  b@acme.com  ", 123],
        "unexpected_field": "should be ignored",
    }
    profile = coerce_profile(raw)
    assert "unexpected_field" not in profile
    assert profile["mail"] == ["a@acme.com", "b@acme.com", "123"]


def test_coerce_profile_stringifies_non_string_text_fields():
    profile = coerce_profile({"mobile_number": 5551234567})
    assert profile["mobile_number"] == "5551234567"
