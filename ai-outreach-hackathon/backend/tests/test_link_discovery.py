from app.pipeline.link_discovery import extract_links, pick_relevant_pages, score_link

HOMEPAGE_HTML = """
<html><body>
<nav>
<a href="/about-us">About Us</a>
<a href="/contact">Contact</a>
<a href="/services">Our Services</a>
<a href="/blog/2024/some-post">Random Blog Post</a>
<a href="https://external.com/about">External About</a>
<a href="#top">Back to top</a>
<a href="mailto:hi@example.com">Email us</a>
<a href="/assets/brochure.pdf">Brochure</a>
</nav>
</body></html>
"""


def test_extract_links_filters_anchors_mailto_and_external():
    links = extract_links(HOMEPAGE_HTML, "https://example.com")
    hrefs = [href for _, href in links]

    assert "https://example.com/about-us" in hrefs
    assert not any("external.com" in href for href in hrefs)
    assert not any(href.startswith("mailto:") for href in hrefs)
    assert not any(href.endswith(".pdf") for href in hrefs)


def test_score_link_ranks_keyword_matches_higher_than_noise():
    about_score = score_link("About Us", "/about-us")
    blog_score = score_link("Random Blog Post", "/blog/2024/some-post")
    assert about_score > blog_score


def test_pick_relevant_pages_prioritizes_about_contact_services():
    def fake_fetch(url: str):
        return None

    picked = pick_relevant_pages("https://example.com", HOMEPAGE_HTML, fake_fetch, limit=5)

    assert any("about" in u for u in picked)
    assert any("contact" in u for u in picked)
    assert any("services" in u for u in picked)
    assert not any("blog" in u for u in picked)


def test_pick_relevant_pages_respects_limit():
    picked = pick_relevant_pages("https://example.com", HOMEPAGE_HTML, lambda u: None, limit=2)
    assert len(picked) <= 2
