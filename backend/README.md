# Backend

This FastAPI backend exposes the following endpoints:
- `POST /analyze` for LLM-based setup analysis
- `POST /pricing` for AWS pricing lookups
- `GET /health` for a simple health check

## Run locally

```bash
cd backend
python -m pip install --upgrade pip
python -m pip install .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment

Copy `.env.example` to `.env` and configure the local-only model settings.

This backend supports only local inference and only `ap-southeast-1` region pricing.

Set:

- `LOCAL_LLM_URL` to a running local inference endpoint
- `LOCAL_LLM_MODEL` to the model ID supported by your local server

For Docker Model Runner with `ai/gemma4:E4B`, use:

```dotenv
LOCAL_LLM_URL=http://host.docker.internal:12434/engines/v1
LOCAL_LLM_MODEL=ai/gemma4:E4B
LLM_PROVIDER=local
DEFAULT_AWS_REGION=ap-southeast-1
```
