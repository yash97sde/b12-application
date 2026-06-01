#!/usr/bin/env python3
import hmac
import hashlib
import json
import requests
from datetime import datetime, timezone

# Configuration
SIGNING_SECRET = "hello-there-from-b12"
B12_URL = "https://b12.io/apply/submission"

def create_payload(name, email, resume_link, repo_link, action_run_link):
    """Create the JSON payload with ISO 8601 timestamp"""
    payload = {
        "action_run_link": action_run_link,
        "email": email,
        "name": name,
        "repository_link": repo_link,
        "resume_link": resume_link,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    }
    # Keys are already sorted alphabetically due to dict literal order in Python 3.7+
    return payload

def compute_signature(payload_json):
    """Compute HMAC-SHA256 signature of the payload"""
    signature = hmac.new(
        SIGNING_SECRET.encode('utf-8'),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def submit_to_b12(name, email, resume_link, repo_link, action_run_link):
    """Submit application to B12"""
    # Create payload
    payload = create_payload(name, email, resume_link, repo_link, action_run_link)
    
    # Convert to compact JSON (no extra whitespace)
    payload_json = json.dumps(payload, separators=(',', ':'), ensure_ascii=False, sort_keys=True)
    
    print(f"Payload: {payload_json}")
    
    # Compute signature
    signature = compute_signature(payload_json)
    print(f"Signature: {signature}")
    
    # Make POST request
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": signature
    }
    
    response = requests.post(B12_URL, data=payload_json.encode('utf-8'), headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"\n✅ SUCCESS!")
            print(f"📝 RECEIPT: {result.get('receipt')}")
            print(f"\nCopy this receipt to confirm your submission.")
            return result.get('receipt')
    else:
        print(f"❌ Submission failed")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 6:
        print("Usage: python submit_b12.py <name> <email> <resume_link> <repo_link> <action_run_link>")
        sys.exit(1)
    
    name = sys.argv[1]
    email = sys.argv[2]
    resume_link = sys.argv[3]
    repo_link = sys.argv[4]
    action_run_link = sys.argv[5]
    
    submit_to_b12(name, email, resume_link, repo_link, action_run_link)
