# AI Outreach Hackathon — Company Insight Enrichment

Scrapes a company's website, cleans and condenses the content, and uses a Gemini model to extract a structured company profile — contact details, core service, target customer, likely pain point, and a personalized outreach opener — ready to drop into a sales/outreach workflow.

## How it works

```
URL in  →  scraper.py       →  crawl homepage + a few relevant internal pages
        →  link_discovery.py → prioritize About/Contact/Services-style links
        →  cleaner.py        → strip boilerplate (nav/footer/script/style), budget total chars
        →  ai_extractor.py   → send cleaned text to Gemini, parse strict JSON response
        →  schema.py         → coerce/validate into a CompanyProfile
        →  storage.py        → upsert into results.json, keyed by source_url
        →  main.py (FastAPI) → /enrich, /results, /health endpoints
```

The extractor is instructed to only use facts present in the scraped text (no hallucinated emails/phones), and `_verify_against_source` in `ai_extractor.py` double-checks the model's returned email/phone against the raw source text before accepting it.

## Project structure

```
ai-outreach-hackathon/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + routes
│   │   ├── config.py          # env-driven settings
│   │   ├── storage.py         # simple JSON-file result store
│   │   └── pipeline/
│   │       ├── scraper.py         # fetches pages, throttled per host
│   │       ├── link_discovery.py  # finds & ranks internal links to crawl
│   │       ├── cleaner.py         # strips boilerplate, builds LLM context
│   │       ├── ai_extractor.py    # calls Gemini, parses + verifies output
│   │       ├── schema.py          # CompanyProfile pydantic schema
│   │       └── orchestrator.py    # ties the pipeline together end-to-end
│   ├── data/results.json      # local result store (dev only)
│   ├── tests/                 # pytest suite
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── index.html
│   ├── app.js                 # calls the API, renders results
│   └── style.css
├── colab/
│   └── hackathon_pipeline.ipynb   # standalone notebook version of the pipeline
└── README.md
```

## Prerequisites

- Python 3.11+
- A Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `requirements.txt` currently lists `google-generativeai==0.8.3`, but `ai_extractor.py` imports from the newer `google-genai` SDK (`from google import genai`). Install the correct package before running:
> ```bash
> pip install google-genai
> ```
> and remove/replace the `google-generativeai` line in `requirements.txt` to avoid confusion.

### Environment variables

Create `backend/.env`:

```env
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-3.6-flash

# Optional — all have sensible defaults, see config.py
DATA_FILE=./data/results.json
SCRAPE_TIMEOUT=10
SCRAPE_RETRIES=2
REQUEST_DELAY=0.6
MAX_PAGES_PER_SITE=5
MAX_CHARS_PER_PAGE=6000
MAX_TOTAL_CHARS=18000
MAX_OUTPUT_TOKENS=1200
SCRAPE_USER_AGENT=Mozilla/5.0 (compatible; CompanyInsightBot/1.0; +https://example.com/bot)
CORS_ORIGINS=*
```

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` in code — **override to `gemini-3.6-flash`**, see note below | Model used for extraction |
| `DATA_FILE` | `backend/data/results.json` | Where enriched profiles are persisted |
| `SCRAPE_TIMEOUT` | `10` | Per-request timeout (seconds) |
| `SCRAPE_RETRIES` | `2` | Retry attempts per page fetch |
| `REQUEST_DELAY` | `0.6` | Minimum delay between requests to the same host |
| `MAX_PAGES_PER_SITE` | `5` | Cap on pages crawled per site |
| `MAX_CHARS_PER_PAGE` | `6000` | Per-page char budget fed to the LLM |
| `MAX_TOTAL_CHARS` | `18000` | Total char budget across all pages |
| `MAX_OUTPUT_TOKENS` | `1200` | Gemini output token cap |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins (lock this down in production) |

> **Model note:** `gemini-2.5-flash` has been deprecated for new users and now returns a 404. Set `GEMINI_MODEL=gemini-3.6-flash` (or the current latest Flash model) in `.env`. Also be aware that Gemini 3.6+ Flash silently ignores custom `temperature`/`top_k`/`top_p` values — `ai_extractor.py` sets `temperature=0`, which will now be a no-op.

### Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`. If the `frontend/` directory exists alongside `backend/`, it's also served as static files at `http://localhost:8000/`.

### Run tests

```bash
pytest
```

## API reference

### `GET /health`
Health check.
```json
{ "status": "ok" }
```

### `POST /enrich`
Scrapes and enriches a single company website.

Request:
```json
{ "url": "https://example.com", "website_name": "Example Co" }
```
`website_name` is optional — used as a fallback label if the model doesn't find a company name.

Response (`CompanyProfile` + metadata):
```json
{
  "website_name": "Example Co",
  "company_name": "Example Co Ltd",
  "address": "",
  "mobile_number": "",
  "mail": ["hello@example.com"],
  "core_service": "...",
  "target_customer": "...",
  "probable_pain_point": "...",
  "outreach_opener": "...",
  "source_url": "https://example.com",
  "label": "Example Co",
  "scraped_at": "2026-08-17T12:00:00+00:00",
  "status": "ok",
  "pages_scraped": ["https://example.com", "https://example.com/about"]
}
```
`status` is one of `ok`, `partial`, `unreachable`, `invalid_url`.

### `GET /results`
Returns all previously enriched profiles (persisted in `DATA_FILE`, upserted by `source_url`).

## Frontend

Static HTML/JS/CSS, no build step. It calls the API at whatever URL is set in the "API base" field in the UI (persisted to `localStorage`), defaulting to the page's own origin when served from the backend, or `http://localhost:8000` when opened as a local file.

Open directly:
```bash
open frontend/index.html
```
or serve it from any static host (see deployment below).

## Deployment

This is a **two-piece deployment** — a stateful-ish Python API and a static frontend — so they're best hosted separately.

### Backend → Render (or Railway / Fly.io)

Vercel's serverless functions have an ephemeral/read-only filesystem, so the JSON-file-based `ResultStore` won't persist data there. Render (or similar) with a normal long-running process works out of the box with no code changes.

1. New Web Service → connect this repo → root directory `backend`
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables (`GEMINI_API_KEY`, `GEMINI_MODEL`, `CORS_ORIGINS`, etc.) in the Render dashboard
5. Optional: attach a persistent disk and set `DATA_FILE` to a path on it, so results survive redeploys

### Frontend → Vercel

1. New Project → root directory `frontend`
2. Framework preset: **Other** (static, no build step)
3. In `frontend/app.js`, set `DEFAULT_API_BASE` to your deployed Render URL (or just paste it into the "API base" field in the running app)
4. Once deployed, set `CORS_ORIGINS` on the Render backend to your Vercel URL, so the browser isn't blocked by CORS

## Colab

`colab/hackathon_pipeline.ipynb` contains a self-contained notebook version of the same scrape → clean → extract pipeline, useful for quick experiments without spinning up the FastAPI server.

## Known limitations

- `ResultStore` is a flat JSON file with a thread lock — fine for a hackathon/demo, not safe for concurrent multi-instance deployments. Swap for a real DB (Postgres, SQLite+WAL, etc.) before scaling.
- No auth on `/enrich` or `/results` — anyone with the URL can call the API and rack up Gemini usage. Add an API key/auth layer before making this public.
- Scraping respects a per-host delay but does not check `robots.txt`.
