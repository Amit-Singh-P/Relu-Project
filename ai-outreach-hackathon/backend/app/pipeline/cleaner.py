import re

from bs4 import BeautifulSoup

STRIP_TAGS = ["script", "style", "noscript", "nav", "footer", "header", "svg", "iframe", "form", "aside", "button"]

_WHITESPACE_RE = re.compile(r"[ \t]+")


def strip_boilerplate(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag_name in STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for attr in ["class", "id", "style"]:
        for tag in soup.find_all(True):
            if tag.has_attr(attr):
                del tag[attr]

    return soup.get_text(separator="\n")


def dedupe_lines(text: str) -> str:
    lines = [_WHITESPACE_RE.sub(" ", line).strip() for line in text.split("\n")]
    lines = [line for line in lines if line]

    seen: set[str] = set()
    unique_lines = []
    for line in lines:
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_lines.append(line)

    return "\n".join(unique_lines)


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " …"


def clean_page(html: str, max_chars: int) -> str:
    stripped = strip_boilerplate(html)
    deduped = dedupe_lines(stripped)
    return truncate(deduped, max_chars)


def build_context(pages: dict[str, str], max_chars_per_page: int, max_total_chars: int) -> str:
    blocks: list[str] = []
    budget = max_total_chars

    for url, html in pages.items():
        if budget <= 0:
            break
        cleaned = clean_page(html, min(max_chars_per_page, budget))
        if not cleaned:
            continue
        block = f"SOURCE: {url}\n{cleaned}"
        blocks.append(block)
        budget -= len(block)

    return "\n\n---\n\n".join(blocks)
