#!/usr/bin/env python3
"""
Docker healthcheck script.
Checks if the Flask application is responding on port 8000.

Optional environment variables:
  - HEALTHCHECK_URL (default: http://127.0.0.1:8000/health)
  - HEALTHCHECK_TIMEOUT (default: 5 seconds)
"""

import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse


DEFAULT_HEALTHCHECK_URL = "http://127.0.0.1:8000/health"
DEFAULT_HEALTHCHECK_TIMEOUT = 5


def _load_timeout():
    """Load the healthcheck timeout value."""
    timeout_value = os.getenv("HEALTHCHECK_TIMEOUT")
    if not timeout_value:
        return DEFAULT_HEALTHCHECK_TIMEOUT
    try:
        return float(timeout_value)
    except ValueError:
        return DEFAULT_HEALTHCHECK_TIMEOUT


def check_health():
    """Check if the application is healthy."""
    healthcheck_url = os.getenv("HEALTHCHECK_URL", DEFAULT_HEALTHCHECK_URL)
    # Validate URL to prevent SSRF attacks
    parsed_url = urlparse(healthcheck_url)
    if (parsed_url.scheme not in {"http", "https"} or 
        parsed_url.hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"} or
        (parsed_url.hostname and (
            parsed_url.hostname.startswith("10.") or
            parsed_url.hostname.startswith("192.168.") or
            parsed_url.hostname.startswith("172.") and 
            16 <= int(parsed_url.hostname.split(".")[1]) <= 31
        ))):
        print(f"Warning: Invalid HEALTHCHECK_URL '{healthcheck_url}', using default", file=sys.stderr)
        healthcheck_url = DEFAULT_HEALTHCHECK_URL
    timeout_seconds = _load_timeout()
    try:
        with urllib.request.urlopen(healthcheck_url, timeout=timeout_seconds) as response:
            if response.status == 200:
                return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        pass
    return False


if __name__ == "__main__":
    sys.exit(0 if check_health() else 1)
