import json
import re

import anthropic

from .. import config
from .schema import coerce_profile, empty_profile

SYSTEM_PROMPT = """You are a precise B2B research analyst that extracts company information strictly from the provided website text.

Rules:
- Use ONLY facts present in the SOURCE text below. Never invent, guess, or infer contact details, names, or services that are not explicitly present.
- If a field cannot be found in the text, return an empty string "" for text fields or an empty array [] for the mail field. Do not use placeholders like "N/A" or "unknown".
- Emails must be copied exactly as they appear in the text.
- Phone numbers must be copied exactly as they appear in the text.
- outreach_opener and probable_pain_point and target_customer may be reasonable business inferences drawn from the described services, but must not fabricate facts (numbers, client names, claims) that are not implied by the text.
- Respond with ONLY a single valid JSON object matching the exact schema below. No markdown fences, no explanation.

Schema:
{
  "website_name": string,
  "company_name": string,
  "address": string,
  "mobile_number": string,
  "mail": string[],
  "core_service": string,
  "target_customer": string,
  "probable_pain_point": string,
  "outreach_opener": string
}"""

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def _parse_json_response(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).rsplit("```", 1)[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {}


EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def _verify_against_source(profile: dict, source_text: str) -> dict:
    source_lower = source_text.lower()

    verified_mail = [m for m in profile.get("mail", []) if m.lower() in source_lower]
    profile["mail"] = verified_mail or [m for m in EMAIL_RE.findall(source_text)][:5]

    phone = profile.get("mobile_number", "")
    if phone:
        digits = re.sub(r"\D", "", phone)
        if digits and digits not in re.sub(r"\D", "", source_text):
            profile["mobile_number"] = ""

    return profile


def call_llm(context_text: str, source_url: str) -> str:
    client = _get_client()
    user_prompt = f"Target website: {source_url}\n\nSOURCE TEXT:\n{context_text}"

    response = client.messages.create(
        model=config.MODEL_NAME,
        max_tokens=config.MAX_OUTPUT_TOKENS,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def extract_profile(context_text: str, source_url: str) -> dict:
    if not context_text.strip():
        return empty_profile()

    try:
        raw_text = call_llm(context_text, source_url)
    except anthropic.APIError:
        return empty_profile()

    parsed = _parse_json_response(raw_text)
    profile = coerce_profile(parsed)
    profile = _verify_against_source(profile, context_text)
    return profile
