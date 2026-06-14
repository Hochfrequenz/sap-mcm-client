# sap-mcm-client

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/sap-mcm-client)](https://pypi.org/project/sap-mcm-client/)
![Supported Python versions](https://img.shields.io/pypi/pyversions/sap-mcm-client.svg)
[![Go Reference](https://pkg.go.dev/badge/github.com/Hochfrequenz/sap-mcm-client.svg)](https://pkg.go.dev/github.com/Hochfrequenz/sap-mcm-client/mcm)
[![Go Report Card](https://goreportcard.com/badge/github.com/Hochfrequenz/sap-mcm-client)](https://goreportcard.com/report/github.com/Hochfrequenz/sap-mcm-client)

![Python Tests](https://github.com/Hochfrequenz/sap-mcm-client/actions/workflows/python-test.yml/badge.svg)
![Python Coverage](https://github.com/Hochfrequenz/sap-mcm-client/actions/workflows/python-coverage.yml/badge.svg)
![Python Lint](https://github.com/Hochfrequenz/sap-mcm-client/actions/workflows/python-lint.yml/badge.svg)
![Python Formatting](https://github.com/Hochfrequenz/sap-mcm-client/actions/workflows/python-formatting.yml/badge.svg)
![Go Tests](https://github.com/Hochfrequenz/sap-mcm-client/actions/workflows/go-test.yml/badge.svg)
![Go Coverage](https://github.com/Hochfrequenz/sap-mcm-client/actions/workflows/go-coverage.yml/badge.svg)
![Go Lint](https://github.com/Hochfrequenz/sap-mcm-client/actions/workflows/go-lint.yml/badge.svg)

Typed Python and Go client for the SAP Cloud for Utilities Foundation Measurement Concept Management (MCM) OData V4 APIs.

## What this does

Provides typed models and an HTTP client that hides the OData V4 protocol behind a clean, domain-specific interface. Instead of constructing raw OData queries with `$expand`, `$filter`, and `$select`, you work with typed Python (Pydantic v2) or Go structs.

## Status

**Alpha.** The type definitions are derived from the [SAP MCM OpenAPI specs](https://api.sap.com/package/SAPCloudForUtilitiesFoundation/overview) (v1.1.0) and have not yet been validated against a live SAP system.

## Supported APIs

All five APIs of the [SAP Cloud for Utilities Foundation](https://api.sap.com/package/SAPCloudForUtilitiesFoundation/overview) package:

| API | Python | Go | Operations | SAP docs |
|---|---|---|---|---|
| Measurement Concept Instance | ✅ | ✅ | CRUD + 4 lifecycle actions + 5 sub-entity updates + 3 notifications | [API guide](https://help.sap.com/docs/Cloud_for_Utilities_Foundation/964850841e2943659444c83c00f05dcc/39d2b485b52c425ba1c5f1121362f239.html?locale=en-US&version=Cloud) · [reference](https://api.sap.com/api/MeasurementConceptInstanceAPI/overview) |
| Measurement Concept Class | ✅ | ✅ | Read-only (list + get) | [reference](https://api.sap.com/api/MCMConceptClass/overview) |
| Measurement Concept Model | ✅ | ✅ | Read-only (list + get) | [reference](https://api.sap.com/api/MCMConceptModel/overview) |
| Instance Migration | ✅ | ✅ | Batch import: migrate + get + list staged + purge + check progress | [API guide](https://help.sap.com/docs/Cloud_for_Utilities_Foundation/39a9e8c04a4943b69d6851aefcdf0f4d/d82eec2df077462f92567971c1279cfa.html?locale=en-US&version=Cloud) |
| Time Series | ✅ | ✅ | 12 read variants + 2 upload + 3 delete | [reference](https://api.sap.com/package/SAPCloudForUtilitiesFoundation/overview) |

Deeper background on the MCM domain itself (Messkonzeptklasse, Messkonzeptmodell, Messkonzeptinstanz):

- [SAP Utilities Core Foundation — Measurement Concept Management](https://help.sap.com/docs/r/product/Cloud_for_Utilities_Foundation/Cloud/en-US) (SAP Help Portal)
- [MCM component overview on community.sap.com](https://community.sap.com/t5/sap-for-utilities-blog-posts/sap-utilities-core-foundation-measurement-concept-management-component/ba-p/13576654)

For a condensed tour of the entity hierarchy and OData conventions, see [`docs/SPECS_ANALYSIS.md`](docs/SPECS_ANALYSIS.md). The SAP OpenAPI specs themselves are not redistributed in this repository (they're SAP IP); see [CONTRIBUTING.md](CONTRIBUTING.md#downloading-the-openapi-specs) for how to download them locally.

## Installation

### Python

```bash
pip install sap-mcm-client
```

PyPI project page: [pypi.org/project/sap-mcm-client](https://pypi.org/project/sap-mcm-client/)

### Go

```bash
go get github.com/Hochfrequenz/sap-mcm-client/mcm
```

Module / API docs: [pkg.go.dev/github.com/Hochfrequenz/sap-mcm-client/mcm](https://pkg.go.dev/github.com/Hochfrequenz/sap-mcm-client/mcm)

## Quickstart

### Python

The Python client is **async** (built on `aiohttp`); call it from within an
event loop and `await` each operation.

```python
import asyncio

from sap_mcm_client import MCMClient, Division, OverallStatus


async def main() -> None:
    async with MCMClient(
        base_url="https://c4u-foundation-mcm-service.cfapps.eu10.hana.ondemand.com",
        token_url="https://mysubaccount.authentication.eu10.hana.ondemand.com/oauth/token",
        client_id="...",
        client_secret="...",
    ) as client:
        # List instances with typed filters — no OData query strings needed
        instances = await client.instances.list(
            division=Division.ELECTRICITY,
            overall_status=OverallStatus.ACTIVE,
            top=50,
        )
        for instance in instances.items:
            print(f"{instance.id_text}: {instance.description}")

        # Fetch one instance with full expansion
        instance = await client.instances.get(
            "01234567-89ab-cdef-0123-456789abcdef",
            include=["all"],
        )
        for metering_location in instance.metering_locations:
            for task in metering_location.metering_tasks:
                print(task.register_code)

        # List classes and models
        classes = await client.classes.list(division=Division.ELECTRICITY)
        models = await client.models.list(include=["market_locations"])


asyncio.run(main())
```

### Go

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/Hochfrequenz/sap-mcm-client/mcm"
)

func main() {
    client := mcm.NewClient(mcm.Config{
        BaseURL: "https://c4u-foundation-mcm-service.cfapps.eu10.hana.ondemand.com",
        Auth: mcm.AuthConfig{
            TokenURL:     "https://mysubaccount.authentication.eu10.hana.ondemand.com/oauth/token",
            ClientID:     "...",
            ClientSecret: "...",
        },
    })

    ctx := context.Background()

    // List instances
    top := 50
    instances, err := client.Instances.List(ctx, &mcm.ListOptions{
        Top:    &top,
        Filter: map[string]string{"division_code": "EL", "overallStatus_code": "ACTIVE"},
    })
    if err != nil {
        log.Fatal(err)
    }
    for _, inst := range instances.Items {
        description := ""
        if inst.Description != nil {
            description = *inst.Description
        }
        fmt.Printf("%s: %s\n", inst.IDText, description)
    }

    // Fetch one instance with full expansion (expansion is automatic on Get)
    inst, err := client.Instances.Get(ctx, "01234567-89ab-cdef-0123-456789abcdef")
    if err != nil {
        if mcm.IsNotFound(err) {
            log.Fatal("instance not found")
        }
        log.Fatal(err)
    }
    fmt.Println(len(inst.MeteringLocations), "metering locations")
}
```

## OAuth2 Configuration

The client authenticates against SAP BTP using the **OAuth2 Client Credentials** flow. You need four values from your SAP subaccount's service binding:

| Value | Example | Where to find it |
|---|---|---|
| `base_url` | `https://c4u-foundation-mcm-service.cfapps.eu10.hana.ondemand.com` | Service binding `url` (in some regions replace `eu10` with `ap10`) |
| `token_url` | `https://<subaccount>.authentication.eu10.hana.ondemand.com/oauth/token` | Service binding `uaa.url` + `/oauth/token` |
| `client_id` | `sb-xsuaa-xxxxx!b12345\|mcm-service!b67890` | Service binding `uaa.clientid` |
| `client_secret` | `<generated secret>` | Service binding `uaa.clientsecret` |

Recommended: store credentials in environment variables and load them via `python-dotenv` (Python) or `os.Getenv` (Go). **Never commit credentials to the repo.**

For the underlying administration details (service instance provisioning, role collections, JWT scopes), see SAP's [Administration Guide for the MCM Component](https://help.sap.com/docs/Cloud_for_Utilities_Foundation/39a9e8c04a4943b69d6851aefcdf0f4d/416202c8d4a449dbae5ac7cdfe40f3c3.html?locale=en-US&version=Cloud).

## Limitations

Be honest about what this client can and can't do today:

- **Not yet validated against a live SAP system.** All models are derived from the OpenAPI specs downloaded from [api.sap.com](https://api.sap.com/package/SAPCloudForUtilitiesFoundation/overview) on 2026-04-13. The real API may have undocumented fields, different error formats, or additional enum values.
- **Test fixtures are spec-derived**, not recorded from real responses. A recording script will close this gap in a future version.
- **Enum values may be incomplete.** The specs list known codes, but the real system may accept additional values. All enums are typed strings so unknown values still deserialize correctly.
- **No batch support yet.** OData `$batch` requests for atomic multi-entity updates are not implemented.

## Error handling

### Python

```python
from sap_mcm_client import MCMClient, MCMNotFoundError, MCMForbiddenError

try:
    instance = await client.instances.get("some-uuid")
except MCMNotFoundError:
    print("Instance does not exist")
except MCMForbiddenError as e:
    print(f"Access denied: {e.detail}")
```

Full exception hierarchy: `MCMAPIError` → `MCMValidationError` (400), `MCMAuthenticationError` (401), `MCMForbiddenError` (403), `MCMNotFoundError` (404). `MCMAuthError` is raised separately when OAuth2 token acquisition fails.

### Go

```go
inst, err := client.Instances.Get(ctx, "some-uuid")
if err != nil {
    switch {
    case mcm.IsNotFound(err):
        fmt.Println("instance does not exist")
    case mcm.IsForbidden(err):
        fmt.Println("access denied")
    default:
        log.Fatal(err)
    }
}
```

## Development

### Python

```bash
pip install -e ".[tests,linting,type_check,formatting]"
tox -e tests        # pytest
tox -e linting      # pylint (10/10 required)
tox -e type_check   # mypy --strict
tox -e coverage     # coverage >= 80%
tox -e spell_check  # codespell
black . && isort .  # auto-format
```

### Go

```bash
go test ./...
golangci-lint run --enable dupl,goconst,gocyclo
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow when updating types from new spec versions, and [CLAUDE.md](CLAUDE.md) for conventions used throughout the codebase.

## License

MIT — see [LICENSE](LICENSE).
