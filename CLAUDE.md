# CLAUDE.md

## Project

Dual-language (Python + Go) typed client for the SAP Cloud for Utilities Foundation MCM OData V4 APIs. The goal is to completely hide OData behind a clean, domain-specific interface.

## Repository Structure

- Go files in repo root (package `mcm`), Python in `src/sap_mcm_client/`
- OpenAPI specs in `specs/`, shared test fixtures in `testdata/`
- CI follows Hochfrequenz template conventions (see `.github/workflows/`)

## Development Commands

### Python
```bash
tox -e tests        # pytest
tox -e linting      # pylint (must score 10/10)
tox -e type_check   # mypy --strict
tox -e coverage     # coverage >= 80%
black . --check && isort . --check  # formatting
```

### Go
```bash
go test ./...
go vet ./...
```

## Key Conventions

### Python
- Python >= 3.11, use `StrEnum` (not `str, Enum`)
- Pydantic v2 with custom alias generator `_to_odata_camel` in `types_common.py` — **do not use `to_camel` directly**, it breaks OData `_code` and `_id` suffixes
- All response models inherit `MCMBaseModel` (frozen=True, extra="ignore")
- All request/update DTOs inherit `MCMRequestModel` (mutable)
- Every field MUST have `Field(description="...")` with text from the OpenAPI spec
- Use `Decimal` for loss factors, coordinates, power values (IEEE754Compatible)
- `max_length` constraints from specs must be preserved

### Go
- Package name: `mcm`
- Pointer types (`*string`, `*int`, `*bool`) for nullable fields
- Custom `Decimal` type in `decimal.go` for IEEE754-compatible JSON
- JSON tags must exactly match the OData wire format
- Doc comments on every exported field, derived from the spec

### Both Languages
- All type definitions are spec-derived (v1.1.0 from api.sap.com, 2026-04-13), not validated against a live SAP system
- Enum values may be incomplete — the API may accept additional codes
- Be transparent about limitations in docstrings and comments

## Code Quality

- Every implementation step MUST be reviewed by an independent agent before moving on
- Best possible typing is a priority — it's the core value of this library
- Docstrings from the OpenAPI specs must be passed through to the library
- No OData terminology in the public API surface
