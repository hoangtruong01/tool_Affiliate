"""
Phase B — End-to-End Workflow Validation Script
Tests: login -> product -> AI analysis -> script -> caption -> asset upload -> video job -> review
"""
import urllib.request
import urllib.error
import urllib.parse
import json
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def api_call(method, path, token=None, json_data=None, form_data=None, multipart=None):
    """Generic API caller with error handling."""
    url = f"{BASE_URL}{path}"
    headers = {}
    body = None

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if json_data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(json_data).encode()
    elif form_data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(form_data).encode()
    elif multipart is not None:
        boundary = "----FormBoundary7MA4YWxkTrZu0gW"
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        lines = []
        for key, (fname, fdata, ftype) in multipart.items():
            lines.append(f"--{boundary}")
            lines.append(f'Content-Disposition: form-data; name="{key}"; filename="{fname}"')
            lines.append(f"Content-Type: {ftype}")
            lines.append("")
            lines.append(fdata)
        lines.append(f"--{boundary}--")
        lines.append("")
        body = "\r\n".join(lines).encode()

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            detail = json.loads(raw)
        except Exception:
            detail = raw
        return e.code, detail


def step(num, label):
    print(f"\n{'='*60}")
    print(f"  STEP {num}: {label}")
    print(f"{'='*60}")


def run():
    results = {}

    # ── Step 1: Login ──
    step(1, "Login")
    code, data = api_call("POST", "/auth/login", json_data={"email": "admin@example.com", "password": "admin123456"})
    if code != 200:
        print(f"  FAIL: HTTP {code} — {data}")
        return
    token = data["access_token"]
    print(f"  ✓ Login OK — token obtained")
    results["login"] = "PASS"

    # ── Step 2: Create Product ──
    step(2, "Create Product")
    code, data = api_call("POST", "/products/", token, json_data={
        "name": "E2E Validation Product",
        "description": "Testing the full AI video pipeline",
        "source_url": "https://example.com/product",
        "category": "Tech"
    })
    if code != 201:
        print(f"  FAIL: HTTP {code} — {data}")
        return
    prod_id = data["id"]
    print(f"  ✓ Product created: {prod_id}")
    results["product"] = "PASS"

    # ── Step 3: AI Analysis ──
    step(3, "AI Product Analysis (Mocked)")
    code, _ = api_call("POST", f"/products/{prod_id}/analyze", token)
    print(f"  Queued: HTTP {code}")
    time.sleep(3)

    code, prod = api_call("GET", f"/products/{prod_id}", token)
    angles = prod.get("selling_angles", [])
    print(f"  ✓ Product status: {prod.get('status')}")
    print(f"  ✓ Selling angles: {len(angles)}")
    if angles:
        angle_id = angles[0]["id"]
        print(f"  ✓ First angle: {angles[0]['title']}")
    else:
        angle_id = None
        print(f"  ⚠ No angles (mock may not have matched)")
    results["analysis"] = "PASS" if len(angles) > 0 else "PARTIAL"

    # ── Step 4: Script Generation ──
    step(4, "AI Script Generation (Mocked)")
    code, _ = api_call("POST", "/scripts/generate", token, json_data={
        "product_id": prod_id,
        "angle_id": angle_id,
        "tone": "casual",
        "platform": "tiktok",
        "duration_seconds": 30
    })
    print(f"  Queued: HTTP {code}")

    script_id = None
    for i in range(15):
        time.sleep(1)
        code, scripts_data = api_call("GET", f"/scripts/?product_id={prod_id}", token)
        items = scripts_data.get("items", [])
        if items:
            script_id = items[0]["id"]
            print(f"  ✓ Script created: {script_id}")
            print(f"  ✓ Hook: {items[0].get('hook', 'N/A')}")
            break

    if not script_id:
        print("  FAIL: Script not generated in 15s")
        results["script"] = "FAIL"
    else:
        results["script"] = "PASS"

    # ── Step 5: Caption Generation ──
    step(5, "AI Caption Generation (Mocked)")
    if script_id:
        code, _ = api_call("POST", "/captions/generate", token, json_data={
            "script_id": script_id,
            "platform": "tiktok"
        })
        print(f"  Queued: HTTP {code}")
        time.sleep(3)

        code, captions = api_call("GET", f"/captions/?script_id={script_id}", token)
        if isinstance(captions, list) and len(captions) > 0:
            print(f"  ✓ Caption created: {captions[0].get('caption_text', 'N/A')[:60]}")
            results["caption"] = "PASS"
        else:
            print(f"  ⚠ No captions found yet (async delay or task error)")
            results["caption"] = "PARTIAL"
    else:
        print("  SKIP: No script_id available")
        results["caption"] = "SKIP"

    # ── Step 6: Asset Upload ──
    step(6, "Asset Upload (Valid Image)")
    
    # Generate a real 1x1 PNG programmatically
    # Smallest possible valid PNG: 8k-ish or just use a real one
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGB', (1, 1), color='red').save(buf, format='PNG')
    valid_png_data = buf.getvalue().decode('latin-1')

    code, asset_data = api_call("POST", "/assets/upload", token, multipart={
        "file": ("test_image.png", valid_png_data, "image/png")
    })
    if code == 201:
        asset_id = asset_data["id"]
        print(f"  ✓ Asset uploaded: {asset_id}")
        results["asset"] = "PASS"
    else:
        print(f"  FAIL: HTTP {code} — {asset_data}")
        asset_id = None
        results["asset"] = "FAIL"

    # ── Step 6.1: Negative Asset Upload (Invalid Image) ──
    step(6.1, "Asset Upload (Invalid Image - Negative Test)")
    code, neg_asset_data = api_call("POST", "/assets/upload", token, multipart={
        "file": ("fake_image.png", "NOT_A_PNG_DATA", "image/png")
    })
    if code == 400:
        print(f"  ✓ Rejected invalid image as expected: {neg_asset_data.get('detail')}")
        results["asset_negative"] = "PASS"
    else:
        print(f"  FAIL: Expected 400, got {code} — {neg_asset_data}")
        results["asset_negative"] = "FAIL"

    # ── Step 7: Video Job Creation ──
    step(7, "Video Job + Render Pipeline")
    if script_id:
        job_payload = {"script_id": script_id, "assets": []}
        if asset_id:
            job_payload["assets"] = [{"asset_id": asset_id, "sequence_order": 0}]

        code, job_data = api_call("POST", "/jobs/", token, json_data=job_payload)
        if code == 201:
            job_id = job_data["id"]
            print(f"  ✓ Job created: {job_id}")
            print(f"  Initial status: {job_data.get('status')}")

            # Wait for render
            final_status = job_data.get("status")
            for i in range(60):
                time.sleep(1)
                code, job = api_call("GET", f"/jobs/{job_id}", token)
                final_status = job.get("status")
                if final_status in ("needs_review", "rendered", "failed"):
                    break

            print(f"  ✓ Final status: {final_status}")
            if job.get("output_path"):
                print(f"  ✓ Output path: {job['output_path']}")
            if job.get("error_message"):
                print(f"  ⚠ Error: {job['error_message']}")

            results["render"] = "PASS" if final_status == "needs_review" else ("PARTIAL" if final_status == "rendered" else "FAIL")

            # ── Step 8: Review Action ──
            if final_status == "needs_review":
                step(8, "Approve/Reject Review Action")
                code, approve_data = api_call("POST", f"/jobs/{job_id}/approve", token, json_data={
                    "decision": "approved",
                    "comment": "E2E test approved"
                })
                if code == 200:
                    print(f"  ✓ Approval: {approve_data}")
                    # Verify final status
                    code, job = api_call("GET", f"/jobs/{job_id}", token)
                    print(f"  ✓ Job status after approval: {job.get('status')}")
                    results["review"] = "PASS" if job.get("status") == "approved" else "PARTIAL"
                else:
                    print(f"  FAIL: HTTP {code} — {approve_data}")
                    results["review"] = "FAIL"
            else:
                results["review"] = "SKIP"
        else:
            print(f"  FAIL: HTTP {code} — {job_data}")
            results["render"] = "FAIL"
            results["review"] = "SKIP"
    else:
        print("  SKIP: No script_id")
        results["render"] = "SKIP"
        results["review"] = "SKIP"

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  PHASE B — VALIDATION SUMMARY")
    print(f"{'='*60}")
    for k, v in results.items():
        icon = "✓" if v == "PASS" else ("⚠" if v in ("PARTIAL", "SKIP") else "✗")
        print(f"  {icon} {k:15s} → {v}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
