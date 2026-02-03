# Quick Start Guide

## Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Run Backend (Without Docker)

Since Docker isn't running, you can start the backend directly:

```bash
# From plevee_backend directory
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

**Note**: The database won't be available without Docker, but the API will still start and you can view the documentation at http://localhost:8000/api/docs

## Run with Docker (Recommended)

When Docker is available:

```bash
# From project root
docker-compose up
```

This will start PostgreSQL, Redis, Backend, and Celery worker.

## API Endpoints

- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/api/docs
- **Sign Up**: POST /api/v1/auth/signup
- **Sign In**: POST /api/v1/auth/signin

## Known Issues

1. **TA-Lib**: Commented out in requirements.txt - requires C library installation
   - To install: `brew install ta-lib` then uncomment in requirements.txt
   
2. **Docker**: If Docker daemon isn't running, start it or run backend directly

## Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (change in production!)
- `REDIS_URL` - Redis connection string
