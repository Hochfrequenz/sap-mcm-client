#!/usr/bin/env python3
"""Record real SAP MCM API responses for fixture validation.

Reads credentials from .env, authenticates with the SAP MCM service,
and saves responses to testdata/recorded/ as JSON.

Usage::

    cp .env.example .env
    # fill in credentials in .env
    pip install httpx python-dotenv
    python scripts/record_responses.py

The recorded responses are committed — they're business data, not
secrets. Only .env itself is gitignored. Diffing the recorded files
against the spec-derived fixtures in testdata/ shows where the real
API differs from the spec.

Note: this is a standalone script, intentionally free of the
sap-mcm-client library so it can run even if the library is broken
or mis-installed.
"""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover
    sys.stderr.write("error: httpx is not installed. Run: pip install httpx python-dotenv\n")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    sys.stderr.write("error: python-dotenv is not installed. Run: pip install httpx python-dotenv\n")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "testdata" / "recorded"

# Full $expand strings mirror what the Python and Go clients send on every Get.
INSTANCE_EXPAND = (
    "meteringLocations($expand=meteringTasks),"
    "marketLocations($expand=calculationRules($expand=steps,usages)),"
    "operandMappings,actors,addresses,"
    "changeProcesses($expand=processData($expand=meteringLocationsPD($expand=meteringTasksPD),"
    "marketLocationsPD,actorsPD($expand=externalReferences)),instanceCharacteristics),"
    "status"
)
CLASS_EXPAND = "classType,division,meteringLocations,actors"
MODEL_EXPAND = (
    "conceptType,measurementClass($expand=meteringLocations,actors),"
    "status,division,modelOperands,"
    "marketLocations($expand=actorsMapping,calculationRules($expand=usages)),"
    "meteringLocationPurposes"
)

MCM_PATH = "/odata/v4/api/mcm/v1"
MIGRATION_PATH = "/odata/v4/api/migrate/v1"


def fetch_token(token_url: str, client_id: str, client_secret: str) -> str:
    """Fetch an OAuth2 access token using client credentials."""
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    response = httpx.post(
        token_url,
        headers={"Authorization": f"Basic {basic}"},
        data={"grant_type": "client_credentials"},
        timeout=30.0,
    )
    response.raise_for_status()
    token: str = response.json()["access_token"]
    return token


def save(name: str, data: Any) -> None:
    """Save a JSON response to testdata/recorded/<name>.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"  wrote {path.relative_to(REPO_ROOT)} ({path.stat().st_size} bytes)")


def get(client: httpx.Client, base_url: str, path: str, **params: Any) -> Any:
    """GET helper — returns parsed JSON or raises with a helpful message."""
    url = f"{base_url}{path}"
    response = client.get(url, params=params)
    if response.status_code >= 400:
        sys.stderr.write(f"  error {response.status_code} on {path}: {response.text[:500]}\n")
        response.raise_for_status()
    return response.json()


def first_id(collection: dict[str, Any]) -> str | None:
    """Return the id of the first item in an OData collection, or None."""
    items = collection.get("value", [])
    if not items:
        return None
    first_item: str = items[0]["id"]
    return first_item


def record(base_url: str, token: str, preset_ids: dict[str, str]) -> None:
    """Record all known API responses."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata.metadata=minimal;IEEE754Compatible=true",
    }
    with httpx.Client(headers=headers, timeout=60.0) as client:
        # --- Classes ---
        print("recording classes...")
        classes = get(client, base_url, f"{MCM_PATH}/MeasurementConceptClasses", **{"$top": 5, "$count": "true"})
        save("class_list", classes)
        class_id = preset_ids.get("class") or first_id(classes)
        if class_id:
            class_get = get(client, base_url, f"{MCM_PATH}/MeasurementConceptClasses({class_id})",
                            **{"$expand": CLASS_EXPAND})
            save("class_get", class_get)
        else:
            print("  no classes found, skipping class_get")

        # --- Models ---
        print("recording models...")
        models = get(client, base_url, f"{MCM_PATH}/MeasurementConceptModels", **{"$top": 5, "$count": "true"})
        save("model_list", models)
        model_id = preset_ids.get("model") or first_id(models)
        if model_id:
            model_get = get(client, base_url, f"{MCM_PATH}/MeasurementConceptModels({model_id})",
                            **{"$expand": MODEL_EXPAND})
            save("model_get", model_get)
        else:
            print("  no models found, skipping model_get")

        # --- Instances ---
        print("recording instances...")
        instances = get(client, base_url, f"{MCM_PATH}/MCMInstances", **{"$top": 5, "$count": "true"})
        save("instance_list", instances)
        instance_id = preset_ids.get("instance") or first_id(instances)
        if instance_id:
            instance_get = get(client, base_url, f"{MCM_PATH}/MCMInstances({instance_id})",
                               **{"$expand": INSTANCE_EXPAND})
            save("instance_get", instance_get)
        else:
            print("  no instances found, skipping instance_get")

        # --- Staged migration instances (read-only, safe to query) ---
        print("recording staged migration instances...")
        try:
            staged = get(client, base_url, f"{MIGRATION_PATH}/StagedMigrationInstances",
                         **{"$top": 5, "$count": "true"})
            save("migration_staged_list", staged)
        except httpx.HTTPStatusError as exc:
            # Forbidden etc. is expected in many tenants — don't abort
            print(f"  skipped ({exc.response.status_code}): {exc.response.text[:200]}")


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")

    required = ["SAP_MCM_BASE_URL", "SAP_MCM_TOKEN_URL", "SAP_MCM_CLIENT_ID", "SAP_MCM_CLIENT_SECRET"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        sys.stderr.write("error: missing required environment variables: " + ", ".join(missing) + "\n")
        sys.stderr.write("copy .env.example to .env and fill in your SAP service binding values\n")
        return 1

    base_url = os.environ["SAP_MCM_BASE_URL"].rstrip("/")
    token_url = os.environ["SAP_MCM_TOKEN_URL"]
    client_id = os.environ["SAP_MCM_CLIENT_ID"]
    client_secret = os.environ["SAP_MCM_CLIENT_SECRET"]

    preset_ids = {
        "instance": os.environ.get("SAP_MCM_INSTANCE_ID", "") or "",
        "class": os.environ.get("SAP_MCM_CLASS_ID", "") or "",
        "model": os.environ.get("SAP_MCM_MODEL_ID", "") or "",
    }

    print(f"authenticating against {token_url}...")
    token = fetch_token(token_url, client_id, client_secret)
    print("  token acquired")

    print(f"recording from {base_url}...")
    print(f"  output directory: {OUTPUT_DIR.relative_to(REPO_ROOT)}")
    record(base_url, token, preset_ids)

    print("\ndone. review and commit the files in testdata/recorded/.")
    print("tip: diff them against the spec-derived fixtures in testdata/ to spot API vs spec gaps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
