# mkv-api-client

Typed Python and Go client for the SAP Cloud for Utilities Foundation Measurement Concept Management (MCM) APIs.

## What this does

Provides typed models and an HTTP client that hides the OData V4 protocol behind a clean, domain-specific interface. Instead of constructing raw OData queries with `$expand`, `$filter`, and `$select`, you work with typed Python (Pydantic) or Go structs.

## Status

**Alpha.** The type definitions are derived from the [SAP MCM OpenAPI specs](https://api.sap.com/package/SAPCloudForUtilitiesFoundation/overview) (v1.1.0) and have not been validated against a live SAP system.

## Limitations

- **No live system validation.** All models are derived from the OpenAPI specs downloaded from api.sap.com on 2026-04-13. The real API may have undocumented fields, different error formats, or additional enum values.
- **Enum values may be incomplete.** The specs list known codes, but the real system may accept additional values. All enums are typed strings so unknown values will still deserialize.
- **Test fixtures are spec-derived.** Our test data is constructed from the OpenAPI spec examples, not recorded from a real SAP system. This means we're testing that our models match the spec, not that the spec matches reality.
- **No batch support yet.** OData `$batch` requests for atomic multi-entity updates are not implemented in v0.1.
- **No TimeSeries or Migration API yet.** These are planned for v0.2.

## Supported APIs

| API | Python | Go | Operations |
|---|---|---|---|
| Measurement Concept Instance | planned | planned | CRUD + 7 lifecycle actions |
| Measurement Concept Class | planned | planned | Read-only |
| Measurement Concept Model | planned | planned | Read-only |
| Instance Migration | v0.2 | v0.2 | Batch import |
| Time Series | v0.2 | v0.2 | Read / Upload / Delete |

## Installation

### Python

```bash
pip install sap-mcm-client
```

### Go

```bash
go get github.com/Hochfrequenz/mkv-api-client
```

## Development

### Python

```bash
pip install -e ".[tests,linting,type_check,formatting]"
tox -e tests        # run tests
tox -e linting      # pylint
tox -e type_check   # mypy --strict
tox -e coverage     # coverage >= 80%
```

### Go

```bash
go test ./...
```

## License

MIT
