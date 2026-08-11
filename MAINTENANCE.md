# ArXiv Daily Project Maintenance Document

## 1. Project Overview
ArXiv Daily is an automated tracking and summarization system for high-energy astrophysics. It monitors new papers on arXiv and Astronomical Telegrams (ATels), scores them based on research interests using AI (Gemini), and generates structured summaries in Markdown.

## 2. Directory Structure
```text
arxiv_daily/
├── .github/          # GitHub Actions (CI/CD)
├── docs/             # MkDocs documentation and generated summaries
│   ├── atels/        # Organized ATel summaries
│   │   ├── sources/  # ATels organized by astronomical object
│   │   ├── index.md  # ATel index
│   │   └── state.json# Last processed ATel ID
│   └── posts/        # Daily arXiv summaries
│       ├── index.md  # ArXiv index
│       └── state.json# Processed ArXiv entry IDs
├── scripts/          # Core Python logic
│   ├── config.py     # Global configuration (API keys, categories, interests)
│   ├── llm_api.py    # AI provider abstraction (Google/OpenAI)
│   ├── main.py       # Main entry point (fetch, process, save)
│   ├── schemas.py    # Pydantic data models for AI structured output
│   └── init_arxiv_state.py # Utility to initialize ArXiv tracking state
├── mkdocs.yml        # MkDocs configuration
└── requirements.txt  # Python dependencies
```

## 3. Core Workflow

### 3.1 ArXiv Processing
1. **Fetch**: Reads the official daily Atom feed for `astro-ph.HE` and
   `astro-ph.SR` in one request. If the feed is unavailable, it falls back to
   the legacy search API with limited retries and a three-second interval.
   The generated note date comes from each feed entry's official announcement
   date (`published`); `--date` is only an explicit manual override.
2. **Keyword Filter**: Pre-filters papers using `KEYWORDS_BROAD`.
3. **AI Score**: Uses `GEMINI_MODEL_LITE` to score papers (0-10) based on `RESEARCH_INTEREST`.
4. **Summarize**: High-score (>=6) papers get a detailed 3-part summary (Background, Data, Conclusion) using `GEMINI_MODEL_FLASH`.
5. **Save**: Generates `Arxiv_Summary_YYYY-MM-DD.md`.

### 3.2 ATel Processing
1. **Sync**: Compares `state.json['last_id']` with ATel RSS.
2. **Scrape**: Fetches full text from `astronomerstelegram.org`.
3. **AI Analyze**: Uses `GEMINI_MODEL_LITE` to extract object name, classification, and summary.
4. **Normalize**: Uses SIMBAD (via `astroquery`) to resolve astronomical object aliases, ensuring same objects are grouped together in `docs/atels/sources/`.
5. **Save**: Updates weekly summaries (`YYYY-WX.md`) and source-specific notes.

## 4. Configuration Reference (`scripts/config.py`)
- **`RESEARCH_INTEREST`**: The "prompt" that guides AI scoring. Update this if your research focus changes.
- **`ARXIV_CATEGORIES`**: List of arXiv categories to monitor.
- **`KEYWORDS_BROAD`**: Initial filter to reduce AI API costs.
- **`API_PROVIDER`**: Toggle between `google` and `openai` (for third-party proxies).
- **`GEMINI_MODEL_FLASH` / `GEMINI_MODEL_LITE`**: Free Google route models.
- **`PAID_MODEL`**: The single model setting used by every paid fallback route.

## 5. Maintenance Tasks
- **Updating Research Interest**: Modify `RESEARCH_INTEREST` in `config.py`.
- **Handling arXiv Errors**: The daily Atom feed is the primary metadata
  source. Keep requests serial and at least three seconds apart when changing
  the legacy API fallback.
- **Handling AI Errors**: If Gemini is congested, the system automatically falls back to OpenAI/Proxy routes as defined in `llm_api.py`.
- **Cleaning State**: If the system misses papers, clear `docs/posts/state.json`.

## 6. Key Operations
- **Daily Run**: `python scripts/main.py --task all`
- **Only ATels**: `python scripts/main.py --task atel`
- **Backfill a missing arXiv range**: `python scripts/main.py --task arxiv --backfill-start 2026-08-01 --backfill-end 2026-08-10`
- **Initialize ArXiv State**: `python scripts/init_arxiv_state.py` (prevents processing very old papers on first run).

`config.py` reads keys from process environment variables; it does not load
`.env` automatically. Before a local run, export the file in the current shell
with `set -a; source .env; set +a`.

Historical RSS/Atom snapshots cannot be requested after the daily feed changes.
The backfill command therefore approximates missing days with the search API's
`submittedDate` field, skips existing daily files, and never replaces a manually
generated report. It leaves 60 seconds between dates and applies 60/180/300-second
cooldowns when the historical endpoint returns HTTP 429. Normal scheduled runs
continue to use the Atom feed's official announcement date.
