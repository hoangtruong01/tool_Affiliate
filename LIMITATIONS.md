# System Limitations — Phase F (MVP)

The AI Video Affiliate Automation Tool is currently in **Phase F (Controlled Live Operations)**. Operators should be aware of the following architectural and functional boundaries.

## 1. Manual Publishing
- **No API Auto-Post**: The system does **not** automatically upload to TikTok or Reels. All publishing is manual.
- **Manual Metrics**: Performance data (views, CTR) must be entered manually by the operator from their platform analytics. There is no automated scraper or API integration for live stats yet.

## 2. Media Storage
- **Local FS Only**: Media is stored on the local filesystem (`/app/media`). There is no S3/Cloud Storage integration.
- **Cleanup Policy**: Orphaned files older than 7 days are automatically deleted. Ensure you download and archive any videos you wish to keep permanently.

## 3. Learning Model
- **Rule-Based Only**: The "Learning" features use simple aggregation and heuristics, not Machine Learning.
- **Data Volume Requirement**: Ranking and retry candidates require at least a small batch of tracked publish events to produce meaningful signals.

## 4. Operational Guardrails
- **Job Timeout**: Any render job taking longer than 60 minutes will be auto-failed by the maintenance system.
- **Single Mode**: The system is designed for a single-operator or small-team workflow. There are no advanced multi-tenant permissions.

## 5. Deployment
- **Not Scaled**: The current Docker Compose setup is optimized for single-node deployment. Running multiple render workers across nodes requires shared storage (NFS/GlusterFS) which is not yet implemented.
