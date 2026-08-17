import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

DATA_FILE = Path(os.environ.get("DATA_FILE", str(BASE_DIR / "data" / "results.json")))

REQUEST_TIMEOUT = float(os.environ.get("SCRAPE_TIMEOUT", "10"))
REQUEST_RETRIES = int(os.environ.get("SCRAPE_RETRIES", "2"))
REQUEST_DELAY = float(os.environ.get("REQUEST_DELAY", "0.6"))

MAX_PAGES_PER_SITE = int(os.environ.get("MAX_PAGES_PER_SITE", "5"))
MAX_CHARS_PER_PAGE = int(os.environ.get("MAX_CHARS_PER_PAGE", "6000"))
MAX_TOTAL_CHARS = int(os.environ.get("MAX_TOTAL_CHARS", "18000"))
MAX_OUTPUT_TOKENS = int(os.environ.get("MAX_OUTPUT_TOKENS", "1200"))

USER_AGENT = os.environ.get(
    "SCRAPE_USER_AGENT",
    "Mozilla/5.0 (compatible; CompanyInsightBot/1.0; +https://example.com/bot)",
)

CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]
