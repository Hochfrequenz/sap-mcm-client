# mkv-api-client

Typed Python and Go client for the SAP Cloud for Utilities Foundation Measurement Concept Management (MCM) OData V4 APIs.

## What this does

Provides typed models and an HTTP client that hides the OData V4 protocol behind a clean, domain-specific interface. Instead of constructing raw OData queries with `$expand`, `$filter`, and `$select`, you work with typed Python (Pydantic v2) or Go structs.

## Status

**Alpha.** The type definitions are derived from the [SAP MCM OpenAPI specs](https://api.sap.com/package/SAPCloudForUtilitiesFoundation/overview) (v1.1.0) and have not yet been validated against a live SAP system.

## Supported APIs

| API | Python | Go | Operations |
|---|---|---|---|
| Measurement Concept Instance | ✅ | ✅ | CRUD + 7 lifecycle actions + 5 sub-entity updates + 3 notifications |
| Measurement Concept Class | ✅ | ✅ | Read-only (list + get) |
| Measurement Concept Model | ✅ | ✅ | Read-only (list + get) |
| Instance Migration | ✅ | ✅ | Batch import: migrate + get + list staged |
| Time Series | ✅ | ✅ | 12 read variants + 2 upload + 3 delete |

## Installation

### Python

```bash
pip install sap-mcm-client
```

### Go

```bash
go get github.com/Hochfrequenz/mkv-api-client
```

## Quickstart

### Python

```python
from sap_mcm_client import MCMClient, Division, OverallStatus

with MCMClient(
    base_url="https://c4u-foundation-mcm-service.cfapps.eu10.hana.ondemand.com",
    token_url="https://mysubaccount.authentication.eu10.hana.ondemand.com/oauth/token",
    client_id="...",
    client_secret="...",
) as client:
    # List instances with typed filters — no OData query strings needed
    instances = client.instances.list(
        division=Division.ELECTRICITY,
        overall_status=OverallStatus.ACTIVE,
        top=50,
    )
    for instance in instances.items:
        print(f"{instance.id_text}: {instance.description}")

    # Fetch one instance with full expansion
    instance = client.instances.get(
        "01234567-89ab-cdef-0123-456789abcdef",
        include=["all"],
    )
    for metering_location in instance.metering_locations:
        for task in metering_location.metering_tasks:
            print(task.register_code)

    # List classes and models
    classes = client.classes.list(division=Division.ELECTRICITY)
    models = client.models.list(include=["market_locations"])
```

### Go

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/Hochfrequenz/mkv-api-client/mcm"
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
        fmt.Printf("%s: %v\n", inst.IDText, inst.Description)
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
    instance = client.instances.get("some-uuid")
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
