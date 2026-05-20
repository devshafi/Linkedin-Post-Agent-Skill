#!/usr/bin/env python3
"""
Post to LinkedIn via Zernio API.
Usage: python3 post-to-linkedin.py <content_file> [config_file]

Reads credentials from linkedin-post-config.md (default: current working directory).
Override config path via the ZERNIO_CONFIG environment variable.
Reads post content from a file to avoid shell encoding issues with emoji.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

DEFAULT_CONFIG = os.path.join(os.getcwd(), "linkedin-post-config.md")
API_URL = "https://api.zernio.com/v1/posts"


def load_config(config_path: str) -> dict:
    config_path = os.environ.get("ZERNIO_CONFIG", config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        text = f.read()

    def extract(pattern, flags=0):
        m = re.search(pattern, text, flags)
        if not m:
            raise ValueError(f"Could not find '{pattern}' in config: {config_path}")
        return m.group(1).strip()

    def extract_optional(pattern, flags=0):
        m = re.search(pattern, text, flags)
        return m.group(1).strip() if m else None

    return {
        "api_key": extract(r"API Key:\s*(\S+)"),
        "profile_id": extract(r"Profile ID:\s*(\S+)"),
        # Use first Account ID entry (Personal Brand Profile)
        "account_id": extract(r"Account ID:\s*([a-f0-9]+)"),
        # Timezone is optional — falls back to UTC if not set
        "timezone": extract_optional(r"Timezone:\s*(\S+)") or "UTC",
    }


def post_to_linkedin(content: str, config: dict) -> dict:
    scheduled = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    payload = {
        "profileId": config["profile_id"],
        "platforms": [{"platform": "linkedin", "accountId": config["account_id"]}],
        "content": content,
        "scheduledFor": scheduled,
        "timezone": config["timezone"],
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 post-to-linkedin.py <content_file> [config_file]")
        sys.exit(1)

    config_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CONFIG
    config = load_config(config_path)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        content = f.read().strip()

    result = post_to_linkedin(content, config)
    print(json.dumps(result, indent=2))
