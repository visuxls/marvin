# Marvin — Agent Guide

Marvin is a personal CFO assistant: a [Pydantic AI](https://pydantic.dev/docs/ai/) agent backed by SQLite financial data, CSV ingestion, live market prices, and a FastAPI web chat UI.

This file is for humans and coding agents working in this repo.

## Stack

- **Python 3.13+** — managed with `uv`
- **Pydantic AI** — agent, tools, Vercel AI UI adapter
- **OpenRouter** — LLM provider (`agent/model.py`)
- **FastAPI** — web app (`app.py`, `web/`)
- **Next.js + AI Elements** — optional React chat UI (`frontend/`)
- **SQLite** — financial data + conversation memory (`data/marvin.db`)
- **yfinance** — live ticker quotes (`services/market_data.py`)
- **pydantic-settings** — config from `.env` (`config/settings.py`)
- **Ruff** — Python formatter and linter
- **ty** — Python type checker (Astral)

## Directory layout

```
agent/              Pydantic AI agent: model, deps, prompt, tools, initialization
config/             Settings (`get_settings()`)
ingestion/          CSV loading and import pipeline
  templates/        First-run demo CSVs and profile (copied to data/ when missing)
models/             Pydantic row models (CSV), summaries (tool outputs), validators
scripts/            CLI entry points (`import_data.py`)
services/           Business logic: market data, valuation, profile, symbol mapping
storage/            SQLite schema, queries, repository, session, conversation memory
web/                FastAPI app with server-side chat persistence
  dependencies.py   FastAPI Depends providers (settings, runtime, UI source)
  lifespan.py       Startup: demo data seed + optional CSV import
  routes/           UI routes (bundled chat HTML)
  memory/           Chat runtime state and API routes
    runtime.py      Agent/model configuration built at app startup
    routes/         /api/chat, /configure, /conversations, /health
  schemas.py        Pydantic request and response models for the web API
frontend/           Next.js chat UI (Vercel AI Elements + useChat)
tests/              Pytest suite with fixtures (`tests/fixtures/`)
data/
  imports/          User CSVs: accounts.csv, balances.csv, holdings.csv
  profile.txt       Personal context for the agent (gitignored)
  profile.example.txt  Template committed to the repo
  marvin.db           SQLite database (gitignored)
app.py                ASGI entry point
```

## Architecture

Data flows in one direction:

```
CSV files  →  ingestion/  →  storage/repository.py  →  SQLite
                                                         ↓
User chat  →  web/memory/routes/  →  agent/tools.py  →  storage/queries.py
                              ↓
                         services/ (valuation, market_data, profile)
```

**Layer rules:**

| Layer | Responsibility | Do not |
|-------|----------------|--------|
| `agent/` | Tool definitions, prompts, agent wiring | Raw SQL, CSV parsing |
| `storage/` | Schema, reads (`queries`), writes (`repository`), sessions | Business logic |
| `services/` | Valuation, market prices, profile loading | Direct agent imports |
| `ingestion/` | CSV → validated rows → upsert | Agent or web concerns |
| `web/` | HTTP, UI, conversation persistence | Financial calculations |
| `models/` | Shared Pydantic types | I/O or side effects |

Keep changes scoped to the right layer. Prefer extending existing functions over adding parallel paths.

## Conventions

### Configuration

- All paths and secrets come from `config.settings.Settings` via `get_settings()`.
- Use `.env` locally; see `.env.example` for required keys.
- Never commit `.env`, `data/marvin.db`, or `data/profile.txt`.
- Pass `settings` or path overrides in tests; do not hardcode `data/` paths in new code.

### Docstrings

Use **Google-style** docstrings on every public function:

```python
def example(arg: str) -> int:
    """Short summary.

    Args:
        arg: What it is.

    Returns:
        What is returned.
    """
```

### Database access

- Use `storage.session.db_connection()` as a context manager.
- Agent tools use `agent.deps.with_db(ctx.deps)` for a scoped connection.
- Schema lives in `storage/db.py`; apply changes there and migrate manually for now (no Alembic).
- Use raw SQL + `sqlite3.Row` — no ORM. Upserts are idempotent.

### CSV ingestion

- Row models live in `models/finance.py` with `Field(alias=...)` matching CSV headers.
- Date parsing uses `models.validators.parse_flexible_date` via `FlexibleDate`.
- Import order: **accounts → balances → holdings → transactions** (`ingestion/importer.py`).
- Rows referencing unknown `account_id` values are skipped with errors in `ImportResult`.
- Re-running import is safe (upsert semantics).
- On first run, `ensure_demo_data()` copies `ingestion/templates/` into `data/imports/` and `data/profile.txt` when those files are missing (existing files are never overwritten).
- On web app startup, `import_all()` runs automatically when `AUTO_IMPORT_ON_STARTUP=true` (default). Results and errors are logged via `log_import_results()`.

### Money and types

- Store money as `TEXT` in SQLite; use `Decimal` in Python models.
- Tool outputs use typed summaries in `models/summaries.py`, not raw dicts.
- Crypto symbols (`BTC`, `ETH`) are mapped to Yahoo tickers in `services/symbols.py`.

### Pydantic AI agent

- Agent is defined in `agent/initialize_agent.py`.
- **Static CFO rules** → `instructions=CFO_INSTRUCTIONS` in `agent/prompt.py` (reinjected every run).
- **Dynamic user profile** → `@agent.system_prompt` calling `profile_system_prompt()`.
- Tools are plain functions registered on the agent; first arg is `RunContext[CFODeps]`.
- Dependencies: `CFODeps(db_path, profile_path)` built by `build_deps()`.
- The agent must use tools for financial numbers — never invent balances or prices.

### Conversation memory

- Persisted in SQLite `conversations` table via `ModelMessagesTypeAdapter` (Pydantic AI standard).
- `web/memory/routes/chat.py` loads server history on reload, saves `result.all_messages()` in `on_complete`.
- Conversation DB reads/writes use `asyncio.to_thread()` so sync SQLite does not block the event loop.
- `conversation_id` comes from the Vercel AI request `id` field.
- Cap: 200 messages per conversation (`MAX_STORED_MESSAGES`).
- Custom web layer replaces bare `agent.to_web()` because the default UI has no server persistence.

### Web app

- **Full stack (recommended):** `./start.sh` — API on :7932 and Next.js UI on :3000
- **API server only:** `uvicorn app:app --host 127.0.0.1 --port 7932`
- **React UI only:** `cd frontend && npm run dev` → http://localhost:3000
- Routes: `/` (bundled UI), `/api/chat`, `/api/configure`, `/api/health`
- FastAPI lifespan in `web/lifespan.py` auto-imports CSVs on startup (when enabled).
- `manage_system_prompt='server'` — passed to `VercelAIAdapter.dispatch_request` so client system prompts are stripped; server owns prompts.
- CORS allows `http://localhost:3000` and `http://127.0.0.1:3000` by default (`CORS_ORIGINS` in `.env`).
- The Next.js frontend uses AI Elements + `useChat` with `DefaultChatTransport` pointed at `/api/chat`.

### Code style

- **Ruff** formats and lints Python code (`pyproject.toml` → `[tool.ruff]`).
- **ty** type-checks Python code (`pyproject.toml` → `[tool.ty]`).
- Minimize scope — smallest correct diff.
- Match existing naming and patterns in the file you edit.
- No over-abstraction (no one-line helpers unless reused).
- Comments only for non-obvious business logic.
- Add tests only when they cover real behavior worth guarding.
- Run `uv run ruff format .` and `uv run ruff check .` before merging.
- Run `uv run ty check` before merging.
- Run `uv run pytest --cov` before merging; 100% coverage is enforced.

## Running locally

```bash
# Install deps (uv)
uv sync

# Copy and fill in secrets
cp .env.example .env

# Copy and customize profile
cp data/profile.example.txt data/profile.txt

# Optional: import CSVs manually (also runs automatically on web app startup)
uv run python -m scripts.import_data

# Frontend one-time setup
cd frontend
cp .env.local.example .env.local
npm install
cd ..

# Start API + Next.js UI (from repo root)
./start.sh
```

## Testing

```bash
uv sync --group dev
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest --cov
```

Coverage is enforced at 100% for application packages (`agent`, `config`, `ingestion`, `models`, `services`, `storage`, `web`, `app`). Tests use temporary databases and `tests/fixtures/` CSVs; external APIs (OpenRouter, yfinance) are mocked.

## Data files

| File | Purpose |
|------|---------|
| `ingestion/templates/*.csv`, `profile.txt` | Demo dataset copied on first run when user files are missing |
| `data/imports/*.example.csv`, `profile.example.txt` | Blank templates for manual setup |
| `data/imports/accounts.csv` | Account metadata (ID, name, type, institution) |
| `data/imports/balances.csv` | Cash/bank balance snapshots by date |
| `data/imports/holdings.csv` | Investment positions (symbol, quantity, average cost per share) |
| `data/imports/transactions.csv` | Cash-flow transactions (optional — delete file to disable; tools return `has_data: false`) |
| `data/profile.txt` | Age, employment, goals — injected into system prompt |

## Agent tools (current)

| Tool | Purpose |
|------|---------|
| `list_accounts` | All accounts |
| `get_account_balances` | Latest balance per account |
| `get_holdings` | Holdings and cost basis |
| `get_ticker_prices` | Live quotes via yfinance |
| `get_holdings_market_value` | Holdings valued at market prices |
| `get_net_worth_summary` | Net worth from cost basis / balances only |
| `get_net_worth_market_value` | Net worth at current market prices |
| `get_balance_history` | Historical balance snapshots by account |
| `get_net_worth_over_time` | Net worth trend from balance history |
| `get_portfolio_allocation` | Portfolio weight by symbol at market prices |
| `get_unrealized_gains` | Per-holding and total unrealized gain/loss |
| `get_liquidity_summary` | Cash vs invested by liquidity category |
| `get_account_breakdown` | Net worth split across accounts |
| `get_transactions` | Filtered transaction list |
| `get_spending_breakdown` | Category spending and income for a date range |
| `get_monthly_burn` | Monthly income, spending, and net burn trend |
| `get_runway_months` | Runway from liquid cash and average monthly burn |
| `get_user_profile` | Reload `data/profile.txt` |
