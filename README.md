# 🎬 AI Video Affiliate Automation Tool

AI-powered platform for creating affiliate marketing videos at scale.

**Stack**: Next.js · FastAPI · PostgreSQL · Redis · n8n · FFmpeg · Celery

---

## 🚀 Quick Start (Local)

### Prerequisites

- Docker Desktop (v4.0+)
- Git

### 1. Clone & Configure

```bash
cd D:\tiktok\tool
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, etc.)
```

### 2. Create Media Directories

```bash
mkdir -p media/uploads media/renders
```

### 3. Start All Services

```bash
docker-compose up --build
```

### 4. Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

### 5. Access Services

| Service               | URL                        |
| --------------------- | -------------------------- |
| Frontend Dashboard    | http://localhost:3000      |
| Backend API (Swagger) | http://localhost:8000/docs |
| n8n Workflows         | http://localhost:5678      |

### 5. Seed Demo Data (Optional)

```bash
docker-compose exec api python -m app.seed_data
```

### 6. Default Admin Login

- Email: `admin@example.com`
- Password: `admin123` (or set via `FIRST_ADMIN_PASSWORD` in `.env`)

---

## Phase C: Stable Review Workflow

Phase C introduces strict status transitions and centralized job management.

### Workflow
1.  **Creation**: Jobs start as `queued`.
2.  **Processing**: Worker picks up job -> `processing`.
3.  **Review**: Render finishes -> `needs_review`.
4.  **Decision**: Admin/Reviewer `approves` or `rejects`.
    - `approved` -> Final state (ready for publish).
    - `rejected` -> Can be `retried` (back to `queued`).
5.  **Failure/Cancel**: 
    - `failed` or `cancelled` jobs can be `retried`.

### Local Setup & Verification
1.  **Seed Data**: Run `python backend/app/seed_data.py` to create a demo environment.
2.  **Running Tests**: `pytest backend/app/test_transitions.py` to verify state machine.
3.  **Manual Check**:
    - [ ] Navigate to `/approvals` to see pending jobs.
    - [ ] Click `Approve` or `Reject` and check `Approval History` tab.
    - [ ] In `/jobs`, verify `Retry` button appears for failed/rejected/cancelled.
    - [ ] Verify `Cancel` button appears for queued/processing.
- **Strict Job Lifecycle**: Centralized status transitions (`queued` -> `processing` -> `rendered` -> `needs_review` -> `approved/rejected`).
- **Control Operations**: `/cancel` and `/retry` endpoints with state-dependent validation.
- **Enhanced Review Flow**: Approval decisions (Approve/Reject) with RBAC enforcement and reviewer metadata persistence.
- **Frontend Dashboard**: Fully functional Jobs page and Approval Queue with video preview and conditional actions.

1. Run `python backend/app/seed_data.py` to populate the database.
2. Access the frontend at `http://localhost:3000`.
3. Try the manual verification checklist below.

### Manual Verification Checklist
- [ ] **Job Transitions**: Attempt to approve a `processing` job via API (should fail).
- [ ] **Approval Flow**: Go to `/approvals`, preview the video, add a comment, and approve.
- [ ] **Cancel/Retry**: Cancel a `queued` job, then retry it.
- [ ] **RBAC**: Verify only `admin` and `reviewer` can perform approval actions.
- [ ] **Error Handling**: Find a `failed` job and verify the `error_message` is displayed in the Jobs page.

---

## 📁 Project Structure

```
├── docker-compose.yml      # All services orchestration
├── .env.example             # Environment template
├── backend/                 # FastAPI + Celery
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── tasks/           # Celery tasks
│   │   └── utils/           # Helpers (JWT, FFmpeg)
│   └── alembic/             # DB migrations
├── frontend/                # Next.js dashboard
│   └── src/
│       ├── app/             # Pages (App Router)
│       ├── components/      # React components
│       ├── lib/             # API client, auth
│       └── types/           # TypeScript types
└── media/                   # Uploads & renders
```

---

## 🛠 Development

### Backend Only

```bash
docker-compose up postgres redis api worker
```

### Frontend Only (requires API running)

```bash
cd frontend && npm run dev
```

### View Celery Logs

```bash
docker-compose logs -f worker
```

### Create New Migration

```bash
docker-compose exec api alembic revision --autogenerate -m "description"
```

---

## 📋 Architecture

- **Frontend**: Next.js 14 App Router, dark-mode dashboard
- **Backend**: FastAPI with async SQLAlchemy, JWT auth, RBAC
- **Queue**: Celery + Redis for AI tasks & video rendering
- **Database**: PostgreSQL 16 with Alembic migrations
- **Media**: FFmpeg for video processing
- **Automation**: n8n for approval workflows & scheduling
