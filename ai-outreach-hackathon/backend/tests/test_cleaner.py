from app.pipeline.cleaner import build_context, clean_page, dedupe_lines, strip_boilerplate, truncate

RAW_HTML = """
<html>
<head><style>.x{color:red}</style><script>track();</script></head>
<body>
<header><nav><a href="/">Home</a><a href="/">Home</a></nav></header>
<main>
<h1>Welcome to Acme</h1>
<p>We build widgets for the modern enterprise.</p>
</main>
<footer>Copyright 2024 Acme Corp. All rights reserved.</footer>
</body>
</html>
"""


def test_strip_boilerplate_removes_script_style_nav_footer():
    text = strip_boilerplate(RAW_HTML)
    assert "track()" not in text
    assert "color:red" not in text
    assert "Copyright" not in text
    assert "Welcome to Acme" in text


def test_dedupe_lines_removes_repeated_nav_items():
    text = "Home\nHome\nAbout\nAbout\nWelcome to Acme"
    deduped = dedupe_lines(text)
    assert deduped.count("Home") == 1
    assert "Welcome to Acme" in deduped


def test_truncate_respects_max_chars():
    long_text = "word " * 500
    truncated = truncate(long_text, 100)
    assert len(truncated) <= 102


def test_clean_page_end_to_end():
    cleaned = clean_page(RAW_HTML, 1000)
    assert "Welcome to Acme" in cleaned
    assert "track()" not in cleaned
    assert "Copyright" not in cleaned


def test_build_context_respects_total_budget():
    pages = {"https://a.com": RAW_HTML, "https://b.com": RAW_HTML}
    context = build_context(pages, max_chars_per_page=1000, max_total_chars=50)
    assert len(context) <= 150
    assert "SOURCE: https://a.com" in context
    assert "SOURCE: https://b.com" not in context
