"""Non-destructive HTTP smoke checks for a running Jeev Rekha API."""

from __future__ import annotations

import json
import os
from urllib.request import urlopen


BASE_URL = os.getenv("SMOKE_API_BASE_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")


def get_json(path: str) -> object:
    with urlopen(f"{BASE_URL}{path}", timeout=10) as response:  # noqa: S310 - operator supplied local URL
        if response.status != 200:
            raise RuntimeError(f"GET {path} returned {response.status}")
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    health = get_json("/health")
    readiness = get_json("/readiness")
    locations = get_json("/locations")
    if not isinstance(health, dict) or health.get("status") != "ok":
        raise RuntimeError("Health response has an unexpected shape")
    if not isinstance(readiness, dict) or readiness.get("status") != "ready":
        raise RuntimeError("Readiness response has an unexpected shape")
    if not isinstance(locations, list):
        raise RuntimeError("Locations response has an unexpected shape")
    print("Smoke checks passed: health, readiness, and locations response shape.")


if __name__ == "__main__":
    main()
