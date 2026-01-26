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
    if not (healthcheck_url.startswith("") or healthcheck_url.startswith("")):
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
