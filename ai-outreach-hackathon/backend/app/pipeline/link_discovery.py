from difflib import SequenceMatcher
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

from bs4 import BeautifulSoup

KEYWORDS: dict[str, list[str]] = {
    "about": ["about", "about-us", "aboutus", "company", "who-we-are", "our-story", "overview"],
    "contact": ["contact", "contact-us", "contactus", "get-in-touch", "reach-us", "support"],
    "services": ["service", "services", "solutions", "products", "what-we-do", "offerings", "platform"],
}

ALL_KEYWORDS = [kw for group in KEYWORDS.values() for kw in group]

SKIP_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".css", ".js",
    ".xml", ".mp4", ".mp3", ".ico", ".webp", ".woff", ".woff2",
)


def _same_domain(url: str, base_netloc: str) -> bool:
    return urlparse(url).netloc.lower().lstrip("www.") == base_netloc.lower().lstrip("www.")


def fetch_sitemap_urls(base_url: str, fetch_fn) -> list[str]:
    candidates = [urljoin(base_url, "/sitemap.xml"), urljoin(base_url, "/sitemap_index.xml")]
    base_netloc = urlparse(base_url).netloc

    for sitemap_url in candidates:
        xml_text = fetch_fn(sitemap_url)
        if not xml_text:
            continue
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError:
            continue

        locs = [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]
        urls = [loc for loc in locs if _same_domain(loc, base_netloc) and not loc.lower().endswith(SKIP_EXTENSIONS)]
        if urls:
            return urls

    return []


def extract_links(html: str, base_url: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    base_netloc = urlparse(base_url).netloc
    seen: set[str] = set()
    links: list[tuple[str, str]] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        full_url = urljoin(base_url, href).split("#")[0]
        if full_url in seen or full_url.lower().endswith(SKIP_EXTENSIONS):
            continue
        if not _same_domain(full_url, base_netloc):
            continue

        seen.add(full_url)
        text = anchor.get_text(" ", strip=True)
        links.append((text, full_url))

    return links


def score_link(text: str, href: str) -> float:
    haystack = f"{text} {href}".lower()
    best = 0.0
    for keyword in ALL_KEYWORDS:
        if keyword in haystack:
            best = max(best, 0.85 + 0.15 * (len(keyword) / max(len(haystack), 1)))
            continue
        ratio = SequenceMatcher(None, keyword, haystack).ratio()
        best = max(best, ratio)
    return best


def pick_relevant_pages(base_url: str, homepage_html: str, fetch_fn, limit: int = 5) -> list[str]:
    ranked: list[str] = []
    seen = {base_url}

    sitemap_urls = fetch_sitemap_urls(base_url, fetch_fn)
    scored_sitemap = sorted(
        ((score_link(url, url), url) for url in sitemap_urls),
        key=lambda pair: pair[0],
        reverse=True,
    )
    for score, url in scored_sitemap:
        if score >= 0.4 and url not in seen:
            ranked.append(url)
            seen.add(url)

    homepage_links = extract_links(homepage_html, base_url)
    scored_links = sorted(
        ((score_link(text, href), href) for text, href in homepage_links),
        key=lambda pair: pair[0],
        reverse=True,
    )
    for score, href in scored_links:
        if score >= 0.4 and href not in seen:
            ranked.append(href)
            seen.add(href)

    return ranked[:limit]
