from datetime import datetime, timezone

from .. import config
from .ai_extractor import extract_profile
from .cleaner import build_context
from .schema import empty_profile
from .scraper import gather_site_pages, normalize_url


def enrich_company(raw_url: str, label: str = "") -> dict:
    url = normalize_url(raw_url)
    now = datetime.now(timezone.utc).isoformat()

    if not url:
        return {
            **empty_profile(),
            "website_name": label,
            "source_url": raw_url,
            "label": label,
            "scraped_at": now,
            "status": "invalid_url",
        }

    pages = gather_site_pages(url)
    if not pages:
        return {
            **empty_profile(),
            "website_name": label,
            "source_url": url,
            "label": label,
            "scraped_at": now,
            "status": "unreachable",
        }

    context_text = build_context(pages, config.MAX_CHARS_PER_PAGE, config.MAX_TOTAL_CHARS)
    profile = extract_profile(context_text, url)

    if label and not profile.get("website_name"):
        profile["website_name"] = label

    status = "ok" if any(v for k, v in profile.items() if k != "website_name") else "partial"

    return {
        **profile,
        "source_url": url,
        "label": label,
        "scraped_at": now,
        "status": status,
        "pages_scraped": list(pages.keys()),
    }
