from typing import Any

from pydantic import BaseModel, Field

SCHEMA_KEYS = [
    "website_name",
    "company_name",
    "address",
    "mobile_number",
    "mail",
    "core_service",
    "target_customer",
    "probable_pain_point",
    "outreach_opener",
]


class CompanyProfile(BaseModel):
    website_name: str = ""
    company_name: str = ""
    address: str = ""
    mobile_number: str = ""
    mail: list[str] = Field(default_factory=list)
    core_service: str = ""
    target_customer: str = ""
    probable_pain_point: str = ""
    outreach_opener: str = ""


def empty_profile() -> dict[str, Any]:
    return CompanyProfile().model_dump()


def coerce_profile(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return empty_profile()

    cleaned: dict[str, Any] = {}
    for key in SCHEMA_KEYS:
        value = data.get(key)
        if key == "mail":
            if isinstance(value, str):
                cleaned[key] = [value] if value.strip() else []
            elif isinstance(value, list):
                cleaned[key] = [str(v).strip() for v in value if str(v).strip()]
            else:
                cleaned[key] = []
        else:
            cleaned[key] = str(value).strip() if value is not None else ""

    try:
        return CompanyProfile(**cleaned).model_dump()
    except Exception:
        return empty_profile()
