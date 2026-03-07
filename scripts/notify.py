#!/usr/bin/env python3
"""Send email notifications from loom via Resend."""

import json
import os
import sys
import urllib.request

RESEND_API_URL = "https://api.resend.com/emails"
SENDER = "max@forgemotionlabs.com"
RECIPIENT = "Max.Schmitz@gmail.com"


def load_api_key():
    key = os.environ.get("RESEND_API_KEY")
    if key:
        return key
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("RESEND_API_KEY="):
                    return line.split("=", 1)[1].strip("'\"")
    return None


def send(subject, body):
    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("RESEND_API_KEY not found in environment or .env")

    payload = json.dumps({
        "from": f"Loom <{SENDER}>",
        "to": [RECIPIENT],
        "subject": subject,
        "text": body,
    }).encode()

    req = urllib.request.Request(
        RESEND_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "loom/1.0",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <subject> <body>")
        sys.exit(1)
    result = send(sys.argv[1], sys.argv[2])
    print(f"Sent: {result.get('id', result)}")
