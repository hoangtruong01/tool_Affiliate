# Phase F Gap Analysis Report

This report summarizes the verification of Phase F — Controlled Live Operations & Learning Loop implementation.

## Fully Implemented
- **Manual Publish Tracking**: `PATCH /jobs/{id}/publish` endpoint and Frontend Tracking Modal.
- **Publish Metadata Fields**: All 5 requested fields (`post_url`, `platform`, `posted_at`, `operator_notes`, `publish_outcome`) are in DB and schemas.
- **Performance Metrics Model & CRUD**: `PerformanceMetric` table with many-to-one relationship to `VideoJob`, associated service, and API endpoints.
- **Learning/Reporting Endpoints**: `/analytics/learning` and `/analytics/reports` providing deep insights into product, hook, and angle performance.
- **Stale Job Cleanup**: Celery task `cleanup_stale_jobs` runs every 30 mins to fail jobs stuck in "processing" for > 1 hour.
- **Orphaned Media Cleanup**: Celery task `cleanup_stale_media` runs weekly to remove unreferenced files > 7 days old.
- **Detailed Health Checks**: `/health/detailed` endpoint monitoring Database and File Storage connectivity.
- **Structured Logging**: Configured in `app/main.py`.
- **Operational Docs**: `RUNBOOK.md` and `LIMITATIONS.md` are comprehensive.

## Partially Implemented
- **Learning UI**: The `Reports` page is functional but only displays a subset of the data returned by `/analytics/learning`. "Retry Candidates" and "Drop Candidates" are shown, but "Failed Jobs" and "Stuck Jobs" from the `/analytics/reports` endpoint are not yet fully integrated into a management view.
- **Frontend Type Safety**: `VideoJob` interface in `jobs/page.tsx` uses `any[]` for metrics and lacks full schema alignment for some Phase F fields.

## Missing
- **None**: All core functional requirements from the Phase F brief are present in the codebase.

## Broken / Inconsistent
- **Timezone Inconsistency**: `app/api/v1/jobs.py:162` uses `datetime.now()` (local) instead of `datetime.now(timezone.utc)`. This will cause "Publish Date" drifts if the server/database aren't in the same zone.
- **Migration Revision Chain**: `alembic/versions/phase_f_v1_initial.py` has `down_revision = None`. If there were previous migrations (MVP), this will cause a conflict during `alembic upgrade head`.

## High-Risk Areas Before Live Pilot
- **Manual Data Entry Burden**: The operator must enter view counts manually. If they enter 1,000,000 instead of 1,000, metrics will be heavily skewed. No basic "reasonableness" check in schemas.
- **Migration Failure**: The revison chain conflict may prevent the production database from applying the Phase F schema changes.

## Recommended Fix Order
1. **Fix Revision Chain**: Ensure `phase_f_v1_initial.py` points to the last MVP revision.
2. **Fix Timezone handling**: Standardize on UTC for all publish timestamps.
3. **Hardify Schemas**: Add basic validation to view counts (e.g., `ge=0`).
4. **UI Polish**: Ensure "Stuck Jobs" are visible to the operator in the Reports page so they know when to manual-fail or investigate.

---
*Verification completed on 2026-03-27*
