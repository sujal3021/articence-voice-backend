# Articence Voice & AI Backend Internship Project

**FastAPI microservice** that ingests concurrent audio metadata packets, orchestrates background AI transcription + sentiment analysis with retry logic for unreliable APIs, and stores results in PostgreSQL.

Built for Articence FastAPI Backend Intern position (Voice & AI Team) — evaluation task completed January 2026.

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
</p>

##  Key Features

- Non-blocking packet ingestion (POST returns **202 Accepted** in <50ms)
- Sequence order validation (logs warnings for missing/out-of-order/duplicates)
- Call state machine: `IN_PROGRESS → PROCESSING_AI → COMPLETED / FAILED`
- Mock AI service with **25% failure rate** + **exponential backoff retries** (tenacity)
- Async PostgreSQL using SQLAlchemy + asyncpg
- Background task processing via FastAPI `BackgroundTasks`
- Dockerized local development (PostgreSQL)
- Alembic migrations

##  Quick Start (2–3 minutes)

```bash
# 1. Clone
git clone https://github.com/sujal_3021/articence-voice-backend.git
cd articence-voice-backend

# 2. Virtual environment
python -m venv articence-env
articence-env\Scripts\activate      # Windows
# source articence-env/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start PostgreSQL
docker compose up -d

# 5. Apply migrations
alembic upgrade head

# 6. Run server
uvicorn app.main:app --reload --port 8000

