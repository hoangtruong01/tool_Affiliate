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

### 6. Default Admin Login

- Email: `admin@example.com`
- Password: (set via `FIRST_ADMIN_PASSWORD` in `.env`)

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
