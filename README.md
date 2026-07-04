# AWS Cost Estimator

A browser-based AWS cost estimation app with a React frontend and FastAPI backend.

The app helps non-technical users describe a target AWS architecture, then uses an LLM to generate estimate rows and fetches pricing data for monthly and yearly cost projections.

## Features

- Describe your target setup in natural language
- LLM-assisted analysis to infer AWS components and services
- Support AWS pricing only for `ap-southeast-1`
- Editable estimate table with quantity, configuration, and assumptions
- Export estimates to an editable Excel file (`.xlsx`)
- Dockerized frontend and backend with `docker-compose`

## Repository layout

- `frontend/` - React + TypeScript + Vite UI
- `backend/` - FastAPI backend API
- `docker-compose.yml` - multi-service orchestration
- `.env.example` - shared environment variables
- `backend/.env.example` - backend-specific environment variables

## Local development

### With Docker Compose

1. Copy the root example env file:

```bash
cp .env.example .env
```

2. Add your secrets in `.env`.
3. Build and start both services:

```bash
docker-compose up --build
```

4. Open the UI at `http://localhost:5173`.

> Note: This repository includes a `model-runner-host` placeholder service in `docker-compose.yml` to document Docker Model Runner host integration. Docker Model Runner itself runs on the host, and the backend uses `host.docker.internal` to communicate with it.

### Frontend only

```bash
cd frontend
npm install
npm run dev
```

The frontend will use `VITE_API_BASE_URL` from `frontend/.env.example` to connect to the backend.

### Backend only

```bash
cd backend
python3 -m pip install --upgrade pip
python3 -m pip install .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment variables

### Root `.env`

- `LOCAL_LLM_URL` - local inference API endpoint for the `local` provider
- `LOCAL_LLM_MODEL` - model ID to send to the local inference service, e.g. `ai/gemma4:E4B`
- `LLM_PROVIDER` - default LLM provider name (`local` only)
- `DEFAULT_AWS_REGION` - region used by default for price lookup (`ap-southeast-1` only)
- `AWS_PRICELIST_API_URL` - AWS Price List Bulk API endpoint

> To use `ai/gemma4:E4B` locally, enable Docker Model Runner on Docker Desktop and set `LOCAL_LLM_URL=http://host.docker.internal:12434/engines/v1`.
>
> This lets the backend call the local Gemma 4 service through Docker Model Runner from inside the container.

> The UI also supports entering a provider key directly per session, so you can select a provider and paste the key in the app without committing it to `.env`.

### Frontend `.env.example`

- `VITE_API_BASE_URL` - backend URL, typically `http://localhost:8000`
- `VITE_DEFAULT_AWS_REGION` - default selected AWS region

### Backend `.env.example`

- `LOCAL_LLM_URL=http://host.docker.internal:12434/engines/v1`
- `LOCAL_LLM_MODEL=ai/gemma4:E4B`
- `LLM_PROVIDER=local`
- `AWS_PRICELIST_API_URL=https://api.pricing.us-east-1.amazonaws.com`
- `DEFAULT_AWS_REGION=ap-southeast-1`

## Security

- No API keys or secrets are hard-coded in source.
- Use environment variables or secret management in deployment.
- Do not commit `.env` or secret files to version control.

## Notes

- The backend exposes `/analyze`, `/pricing`, and `/export` endpoints.
- The frontend can fall back to client-side TSV export if needed, but the preferred export is `.xlsx` via backend.
- The app uses only local model support with `ai/gemma4:E4B` via Docker Model Runner.
