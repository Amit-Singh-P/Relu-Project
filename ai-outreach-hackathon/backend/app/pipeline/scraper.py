import time

import requests

from .. import config

_session = requests.Session()
_session.headers.update({"User-Agent": config.USER_AGENT})

_last_request_at: dict[str, float] = {}


def _throttle(host: str) -> None:
    last = _last_request_at.get(host, 0.0)
    wait = config.REQUEST_DELAY - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)
    _last_request_at[host] = time.monotonic()


def fetch_url(url: str, timeout: float | None = None, retries: int | None = None) -> str | None:
    timeout = timeout if timeout is not None else config.REQUEST_TIMEOUT
    retries = retries if retries is not None else config.REQUEST_RETRIES

    from urllib.parse import urlparse
    host = urlparse(url).netloc

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        _throttle(host)
        try:
            response = _session.get(url, timeout=timeout, allow_redirects=True)
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(min(2 ** attempt, 4))
            continue

        if response.status_code == 429 or response.status_code >= 500:
            last_error = RuntimeError(f"HTTP {response.status_code}")
            time.sleep(min(2 ** attempt, 4))
            continue

        if response.status_code >= 400:
            return None

        content_type = response.headers.get("Content-Type", "")
        if "text" not in content_type and "xml" not in content_type and content_type:
            return None

        return response.text

    if last_error:
        return None
    return None


def normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        return raw_url
    if not raw_url.lower().startswith(("http://", "https://")):
        raw_url = f"https://{raw_url}"
    return raw_url.rstrip("/")


def gather_site_pages(base_url: str, limit: int | None = None) -> dict[str, str]:
    from .link_discovery import pick_relevant_pages

    limit = limit if limit is not None else config.MAX_PAGES_PER_SITE

    homepage_html = fetch_url(base_url)
    if not homepage_html:
        return {}

    pages = {base_url: homepage_html}

    relevant_urls = pick_relevant_pages(base_url, homepage_html, fetch_url, limit=limit)
    for url in relevant_urls:
        if len(pages) >= limit:
            break
        html = fetch_url(url)
        if html:
            pages[url] = html

    return pages
