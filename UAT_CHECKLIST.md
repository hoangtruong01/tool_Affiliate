# Phase F — User Acceptance Testing (UAT) Checklist

Use this checklist to verify that the system is ready for the Phase F Live Pilot. Execute these steps as an operator to ensure the "Learning Loop" is functional.

### 1. Script & Render Workflow
- [ ] **Step 1: Approve Script**
  - Go to `/approvals` and approve a generated script for a real product.
- [ ] **Step 2: Create Render Job**
  - Go to `/jobs`, click **New Render Job**, select the approved script and visual assets.
- [ ] **Step 3: Verify Render Success**
  - Wait for the status to reach `approved` (or `needs_review` if workflow requires).
  - Open the **Preview** modal and watch the video.

### 2. Manual Publishing & Tracking
- [ ] **Step 4: Publish Manually**
  - Download the video.
  - Manually post to TikTok/Reels/Shorts using the Asset Bundle for copy/paste.
- [ ] **Step 5: Log Publish Metadata**
  - In `/jobs`, click **Track Publishing** (Share icon) on the job.
  - Enter the live **Post URL**, **Platform**, and **Publish Outcome**.
  - Verify status changes to `published`.

### 3. Performance & Learning Loop
- [ ] **Step 6: Enter 24h Metrics**
  - Wait for 24 hours (or simulate).
  - Click **Add Performance Snapshot** (Chart icon) on the published job.
  - Enter views, CTR, and an **Operator Rating** (1-5).
- [ ] **Step 7: Verify Learning Output**
  - Go to the **Learning & Reports** page.
  - Verify the product/hook now appears in "Top Products" or "Top Hooks" (if ratings were high).
  - Verify if it appears in "Candidates to Retry" if views/rating were mediocre.
- [ ] **Step 8: Verify Bottleneck Monitoring**
  - (Simulated) Check the bottom of the Reports page for any **Stuck Jobs** (if any renders have been running >30m).

---
*Checked by: [Operator Name]*
*Date: 2026-03-27*
