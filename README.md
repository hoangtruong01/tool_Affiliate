# 🎬 AI Video Affiliate Automation Tool

AI-powered platform for creating affiliate marketing videos at scale.

**Stack**: Next.js · FastAPI · PostgreSQL · Redis · Celery · FFmpeg

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (v4.0+)
- Git

### 1. Clone & Configure
```bash
cd D:\tiktok\tool
cp .env.example .env
# Edit .env: set OPENAI_API_KEY (or leave default for mock mode)
```

### 2. Start Services
```bash
docker compose up --build -d
```

### 3. Run Database Migrations
```bash
docker compose exec api alembic upgrade head
```

### 4. Seed Demo Data
```bash
docker compose exec api python -m app.seed_data
```

### 5. Access
| Service            | URL                         |
|--------------------|-----------------------------|
| Backend API (Docs) | http://localhost:8000/docs   |
| Frontend Dashboard | http://localhost:3000        |

### 6. Login
- **Email**: `admin@example.com`
- **Password**: `admin123`

---

## 📋 Phase C: Job Lifecycle & Review Workflow

### Status Machine
```
queued → processing → needs_review → approved
                  ↘ failed           ↘ rejected
                  ↘ cancelled
```

**Allowed transitions:**
| From           | To                                    |
|----------------|---------------------------------------|
| `queued`       | `processing`, `cancelled`, `failed`   |
| `processing`   | `needs_review`, `failed`, `cancelled` |
| `needs_review` | `approved`, `rejected`, `failed`      |
| `approved`     | `published`                           |
| `rejected`     | `queued` (via retry)                  |
| `failed`       | `queued` (via retry)                  |
| `cancelled`    | `queued` (via retry)                  |

### API Operations
| Endpoint                       | Who            | When                       |
|--------------------------------|----------------|----------------------------|
| `POST /jobs/{id}/approve`      | admin/reviewer | Status is `needs_review`   |
| `POST /jobs/{id}/cancel`       | admin/reviewer | Status is `queued`/`processing` |
| `POST /jobs/{id}/retry`        | any user       | Status is `failed`/`rejected`/`cancelled` |

### Operator Guide

**Daily workflow:**
1. Seed or create products → AI analysis → script generation → render job.
2. Jobs auto-transition: `queued` → `processing` → `needs_review`.
3. Go to `/approvals` → preview video → approve or reject.
4. Rejected jobs can be retried from `/jobs`.
5. Failed jobs show `error_message` for debugging.

**Runtime Configuration (Mock vs Real):**
To develop locally without incurring API or CPU costs, configure your `.env` or `config.py`:
- `MOCK_AI_SERVICES=True`: Returns standardized JSON without querying OpenAI.
- `MOCK_RENDER_PROVIDER=True`: Skips FFmpeg and creates a stub .mp4 for pipeline testing.

**Daily Automation Setup:**
The `beat` Docker service runs a Celery Beat scheduler.
- **Action**: Picks an active product daily (9:00 AM UTC) and triggers a casual TikTok script generation task for the operator.
- **Logs**: Follow with `docker compose logs -f beat`.

**Running tests:**
```bash
docker compose exec api python -m app.test_transitions   # Status machine tests
docker compose exec api python -m app.test_workflow       # E2E workflow test
```

### Known Limitations
- `rendered` status still exists in the DB enum but is unused (kept for backward compat).
- Double-approve is a no-op (same-state returns silently).
- Publishing endpoints (`/publish/tiktok`, `/publish/shopee`) are stubbed.
- Frontend requires the frontend Docker container or `npm run dev` separately.
- n8n integration is disabled for MVP.

---

## 📁 Project Structure
```
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── tasks/           # Celery tasks
│   │   └── utils/           # JWT, FFmpeg, security
│   └── alembic/             # DB migrations
├── frontend/                # Next.js dashboard
│   └── src/app/             # Pages (App Router)
└── media/                   # Uploads & renders
```

## 🛠 Development

```bash
# Backend only
docker compose up postgres redis api worker

# Frontend dev (requires API running)
cd frontend && npm run dev

# View worker logs
docker compose logs -f worker
```

## 📐 Architecture
- **Frontend**: Next.js 14 App Router, dark-mode dashboard
- **Backend**: FastAPI with async SQLAlchemy, JWT auth, RBAC
- **Queue**: Celery + Redis for AI tasks & video rendering
- **Database**: PostgreSQL 16 with Alembic migrations
- **Media**: FFmpeg for video processing
