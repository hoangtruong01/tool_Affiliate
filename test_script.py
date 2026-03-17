import subprocess
import json
import json.decoder

try:
    auth_resp = subprocess.check_output([
        "curl", "-s", "-X", "POST", "http://localhost:8000/api/v1/auth/login",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "-d", "username=admin@example.com&password=admin123456"
    ])
    token = json.loads(auth_resp.decode('utf-8'))['access_token']
    print(f"Token: {token[:10]}...")

    prod_resp = subprocess.check_output([
        "curl", "-s", "-X", "POST", "http://localhost:8000/api/v1/products/",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", '{"name": "Sample Product", "description": "An amazing sample product for testing", "source_url": "https://example.com/product", "category": "Technology"}'
    ])
    print("Product Result:")
    print(json.loads(prod_resp.decode('utf-8')))
except Exception as e:
    print(f"Error: {e}")
