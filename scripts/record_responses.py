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

Exit codes
----------

- 0: all attempted recordings succeeded (or were gracefully skipped).
- 1: missing or invalid configuration (bad .env, unreachable host).
- 2: authentication failed (bad credentials, token endpoint returned an error).
- 3: one or more recordings failed with an unexpected error (others may
     have succeeded; see the log for details).
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


class ConfigError(Exception):
    """Raised for invalid or missing configuration."""


class AuthError(Exception):
    """Raised when OAuth2 token acquisition fails."""


class RecordingError(Exception):
    """Raised when recording a specific endpoint fails unexpectedly."""


def fetch_token(token_url: str, client_id: str, client_secret: str) -> str:
    """Fetch an OAuth2 access token using client credentials.

    Raises ConfigError on network/DNS/TLS issues and AuthError on HTTP errors
    or malformed responses.
    """
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    try:
        response = httpx.post(
            token_url,
            headers={"Authorization": f"Basic {basic}"},
            data={"grant_type": "client_credentials"},
            timeout=30.0,
        )
    except httpx.ConnectError as exc:
        raise ConfigError(f"cannot reach token endpoint {token_url}: {exc}") from exc
    except httpx.TimeoutException as exc:
        raise ConfigError(f"timeout reaching token endpoint {token_url}: {exc}") from exc
    except httpx.RequestError as exc:
        raise ConfigError(f"network error reaching token endpoint {token_url}: {exc}") from exc

    if response.status_code >= 400:
        raise AuthError(
            f"token endpoint returned {response.status_code}: {response.text[:500]}\n"
            "check SAP_MCM_CLIENT_ID and SAP_MCM_CLIENT_SECRET in .env"
        )
    try:
        payload = response.json()
    except ValueError as exc:
        raise AuthError(f"token endpoint returned non-JSON body: {response.text[:200]}") from exc
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise AuthError(f"token endpoint response missing 'access_token': {payload}")
    return token


def save(name: str, data: Any) -> None:
    """Save a JSON response to testdata/recorded/<name>.json.

    Raises RecordingError if the output directory can't be created
    or the file can't be written (permissions, disk full, etc.).
    """
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / f"{name}.json"
        path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    except OSError as exc:
        raise RecordingError(f"cannot write {name}.json: {exc}") from exc
    print(f"  wrote {path.relative_to(REPO_ROOT)} ({path.stat().st_size} bytes)")


def get(client: httpx.Client, base_url: str, path: str, **params: Any) -> Any:
    """GET helper — returns parsed JSON.

    Raises httpx.HTTPStatusError on 4xx/5xx so the caller can decide
    whether to abort or skip. Raises RecordingError on unexpected
    non-HTTP failures (network errors, malformed JSON).
    """
    url = f"{base_url}{path}"
    try:
        response = client.get(url, params=params)
    except httpx.RequestError as exc:
        raise RecordingError(f"network error on GET {path}: {exc}") from exc

    if response.status_code >= 400:
        sys.stderr.write(f"  error {response.status_code} on {path}: {response.text[:500]}\n")
        response.raise_for_status()

    try:
        return response.json()
    except ValueError as exc:
        raise RecordingError(f"GET {path} returned non-JSON body: {response.text[:200]}") from exc


def first_id(collection: dict[str, Any]) -> str | None:
    """Return the id of the first item in an OData collection, or None."""
    items = collection.get("value", [])
    if not items:
        return None
    first_item: str = items[0]["id"]
    return first_item


def _record_pair(
    client: httpx.Client,
    base_url: str,
    label: str,
    list_path: str,
    get_path_template: str,
    expand: str,
    preset_id: str,
    failures: list[str],
) -> None:
    """Record a list + single-entity pair for one resource.

    Appends an entry to ``failures`` if the recording fails unexpectedly,
    so the caller can continue with other resources.
    """
    print(f"recording {label}...")
    try:
        collection = get(client, base_url, list_path, **{"$top": 5, "$count": "true"})
    except httpx.HTTPStatusError as exc:
        msg = f"{label} list: HTTP {exc.response.status_code}"
        sys.stderr.write(f"  {msg}\n")
        failures.append(msg)
        return
    except RecordingError as exc:
        sys.stderr.write(f"  {label} list failed: {exc}\n")
        failures.append(f"{label} list: {exc}")
        return

    try:
        save(f"{label}_list", collection)
    except RecordingError as exc:
        sys.stderr.write(f"  {label} list save failed: {exc}\n")
        failures.append(f"{label} list save: {exc}")
        return

    entity_id = preset_id or first_id(collection)
    if not entity_id:
        print(f"  no {label} found, skipping {label}_get")
        return

    try:
        entity = get(client, base_url, get_path_template.format(id=entity_id), **{"$expand": expand})
    except httpx.HTTPStatusError as exc:
        msg = f"{label} get({entity_id}): HTTP {exc.response.status_code}"
        sys.stderr.write(f"  {msg}\n")
        failures.append(msg)
        return
    except RecordingError as exc:
        sys.stderr.write(f"  {label} get({entity_id}) failed: {exc}\n")
        failures.append(f"{label} get: {exc}")
        return

    try:
        save(f"{label}_get", entity)
    except RecordingError as exc:
        sys.stderr.write(f"  {label} get save failed: {exc}\n")
        failures.append(f"{label} get save: {exc}")


def record(base_url: str, token: str, preset_ids: dict[str, str]) -> list[str]:
    """Record all known API responses. Returns a list of failure messages."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata.metadata=minimal;IEEE754Compatible=true",
    }
    failures: list[str] = []
    with httpx.Client(headers=headers, timeout=60.0) as client:
        _record_pair(
            client,
            base_url,
            "class",
            f"{MCM_PATH}/MeasurementConceptClasses",
            f"{MCM_PATH}/MeasurementConceptClasses({{id}})",
            CLASS_EXPAND,
            preset_ids.get("class", ""),
            failures,
        )
        _record_pair(
            client,
            base_url,
            "model",
            f"{MCM_PATH}/MeasurementConceptModels",
            f"{MCM_PATH}/MeasurementConceptModels({{id}})",
            MODEL_EXPAND,
            preset_ids.get("model", ""),
            failures,
        )
        _record_pair(
            client,
            base_url,
            "instance",
            f"{MCM_PATH}/MCMInstances",
            f"{MCM_PATH}/MCMInstances({{id}})",
            INSTANCE_EXPAND,
            preset_ids.get("instance", ""),
            failures,
        )

        # Staged migration instances — many tenants don't have the migration
        # component enabled; 403/404 is expected there and is not a failure.
        print("recording staged migration instances...")
        try:
            staged = get(
                client,
                base_url,
                f"{MIGRATION_PATH}/StagedMigrationInstances",
                **{"$top": 5, "$count": "true"},
            )
            try:
                save("migration_staged_list", staged)
            except RecordingError as exc:
                sys.stderr.write(f"  migration staged save failed: {exc}\n")
                failures.append(f"migration staged save: {exc}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (403, 404):
                print(f"  skipped (HTTP {exc.response.status_code}) — migration component not enabled")
            else:
                msg = f"migration staged list: HTTP {exc.response.status_code}"
                sys.stderr.write(f"  {msg}\n")
                failures.append(msg)
        except RecordingError as exc:
            sys.stderr.write(f"  migration staged list failed: {exc}\n")
            failures.append(f"migration staged list: {exc}")

    return failures


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
    try:
        token = fetch_token(token_url, client_id, client_secret)
    except ConfigError as exc:
        sys.stderr.write(f"configuration error: {exc}\n")
        return 1
    except AuthError as exc:
        sys.stderr.write(f"authentication failed: {exc}\n")
        return 2
    print("  token acquired")

    print(f"recording from {base_url}...")
    print(f"  output directory: {OUTPUT_DIR.relative_to(REPO_ROOT)}")
    failures = record(base_url, token, preset_ids)

    if failures:
        sys.stderr.write("\nrecording completed with errors:\n")
        for msg in failures:
            sys.stderr.write(f"  - {msg}\n")
        sys.stderr.write("partial output written; review testdata/recorded/ before committing\n")
        return 3

    print("\ndone. review and commit the files in testdata/recorded/.")
    print("tip: diff them against the spec-derived fixtures in testdata/ to spot API vs spec gaps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
