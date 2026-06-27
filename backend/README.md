# Backend API

FastAPI backend for the trading and backtesting application. Sprint 1 provides authentication infrastructure via Supabase JWT verification, CORS, and a health check endpoint.

## Prerequisites

- Python 3.11+
- A Supabase project with Auth enabled

## Local Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your Supabase project values:

- `SUPABASE_URL` — from Supabase project settings
- `SUPABASE_JWT_SECRET` — from Supabase API settings (JWT secret)
- `SUPABASE_ANON_KEY` — optional in Sprint 1; used in Sprint 2 for database access

Start the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path         | Auth       | Description                    |
|--------|--------------|------------|--------------------------------|
| GET    | `/health`    | None       | Service health check           |
| GET    | `/api/v1/me` | Bearer JWT | Current user from JWT claims   |

## Verifying Auth

Obtain an access token from Supabase Auth (via the frontend or Supabase dashboard), then:

```bash
curl http://localhost:8000/health

curl http://localhost:8000/api/v1/me
# → 401

curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/v1/me
# → 200 with user id, email, role
```

## Running Tests

```bash
cd backend
pytest
```

## Deployment

### Railway

1. Create a new service and set the root directory to `backend/`
2. Add environment variables from `.env.example`
3. Railway reads `railway.toml` for the start command and health check

### Render

1. Create a Web Service with root directory `backend/`
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`

## Architecture Notes

- User registration and login are handled by Supabase Auth on the frontend
- The backend verifies Supabase-issued JWTs locally via JWKS (with HS256 fallback for legacy projects)
- PostgreSQL is deferred to Sprint 2 when strategy and backtest data models are introduced
