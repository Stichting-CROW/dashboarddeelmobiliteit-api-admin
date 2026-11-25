import os

import requests
from fastapi import HTTPException

# The validator itself stops after 55 seconds and then still responds.
VALIDATOR_TIMEOUT_SECONDS = 65


def validate(config: dict) -> dict:
    """Sends a feed configuration to the feed validator service (dd-importer-v2
    cmd/feed_validator) and returns its result."""
    url = os.getenv("FEED_VALIDATOR_URL")
    token = os.getenv("FEED_VALIDATOR_TOKEN")
    if not url or not token:
        raise HTTPException(status_code=503, detail="feed validator is not configured")

    try:
        response = requests.post(
            url.rstrip("/") + "/validate",
            json=config,
            headers={"X-Feed-Validator-Token": token},
            timeout=VALIDATOR_TIMEOUT_SECONDS,
        )
    except requests.RequestException as e:
        print("Feed validator not reachable:", type(e).__name__)
        raise HTTPException(status_code=502, detail="feed validator is not reachable")
    if response.status_code != 200:
        print("Feed validator responded with status", response.status_code)
        raise HTTPException(status_code=502, detail="feed validator returned an error")
    return response.json()
