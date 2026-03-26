# Production Readiness Checklist

This checklist ensures the AI Video Affiliate Tool is ready for real-world deployment.

## 1. Security & Auth
- [ ] Change `JWT_SECRET_KEY` to a 256-bit random string.
- [ ] Change `FIRST_ADMIN_PASSWORD` from default.
- [ ] Ensure `allow_origins` in `main.py` is restricted to your production domain.
- [ ] Run backend behind an HTTPS reverse proxy (Nginx/Caddy).

## 2. Infrastructure
- [ ] Switch `MOCK_AI_SERVICES` to `False`.
- [ ] Switch `MOCK_RENDER_PROVIDER` to `False`.
- [ ] Configure persistent volumes for `/app/media` and PostgreSQL data.
- [ ] Set up a dedicated Redis instance (not shared with other apps).

## 3. Scaling
- [ ] Deploy multiple `worker` containers to handle concurrent renders.
- [ ] Use `gunicorn` or `uvicorn` with multiple workers for the `api` service.
- [ ] Monitor disk space for the `renders/` directory.

## 4. External APIs
- [ ] Valid OpenAI/Gemini API key provided.
- [ ] TikTok/Shopee developer account credentials (for future Phase F).
- [ ] n8n webhook URL verified and active.

## 5. Maintenance
- [ ] Set up a cron job or Celery Beat for `cleanup_stale_jobs` (already included in `app.worker`).
- [ ] Configure logs rotation to prevent disk pressure.
