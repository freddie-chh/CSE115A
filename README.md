# Trading App Monorepo

Monorepo for a trading and backtesting application.

## Projects

- **[backend/](backend/)** — FastAPI API with Supabase JWT authentication (Sprint 1)

Frontend scaffolding is planned for a future sprint.

## Quick Start (Backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

See [backend/README.md](backend/README.md) for full setup, deployment, and API documentation.
