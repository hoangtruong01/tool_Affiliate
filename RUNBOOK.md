# Operational Runbook — Phase F

This document outlines the standard operating procedures for the AI Video Affiliate Automation Tool in its current Phase F state.

## 1. Daily Operator Workflow

### Scripting & Product Selection
1. **Analyze Intelligence**: Check the **Learning & Reports** tab to see which products and hooks are performing best.
2. **Select Product**: Go to **Products**, select a high-performer or a new test candidate.
3. **Generate & Approve**: Generate scripts, edit if necessary, and mark as **Approved**.

### Rendering
1. **Queue Render**: In **Video Jobs**, click "New Render Job", select an approved script and relevant assets.
2. **Quality Control**: Wait for status "Needs Review". Preview the video.
3. **Approve/Reject**: If acceptable, mark as **Approved**. If not, mark as **Rejected** and retry with different assets.

### Publishing & Tracking
1. **Download**: Download the approved video MP4.
2. **Manual Publish**: Upload to TikTok/Reels/Shorts manually.
3. **Log Publish**: Immediately click the **Share** (purple) button on the job row.
   - Enter the Platform (e.g., TikTok).
   - Paste the Live Post URL.
   - Set the Publish Date.
   - Add initial Operator Notes (e.g., "Posted with trending audio X").

### Performance Feedback
1. **24h Check-in**: After 24-48 hours, return to the job.
2. **Log Metrics**: Click the **Bar Chart** (emerald) button on the job row.
   - Enter views, conversions, CTR.
   - Assign an **Operator Rating** (1-5) based on engagement quality.
3. **Learning Loop**: The system will automatically aggregate these signals into the **Command Center** and **Reports** page for the next batch.

## 2. Maintenance Tasks

The system runs several automated tasks via Celery:
- **Daily Content Generation (9:00 AM UTC)**: Auto-generates initial drafts for active products.
- **Stale Job Cleanup (Every 30m)**: Auto-fails jobs stuck in "processing" for >1 hour.
- **Orphaned Media Cleanup (Sundays 3:00 AM UTC)**: Deletes local files >7 days old that aren't linked to any active database record.

## 3. Monitoring

- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /health/detailed` (Checks DB and Media storage accessibility).
- **Logs**: Check container logs for `[StaleJobs]` and `[MediaCleanup]` prefixes for maintenance audit trails.
