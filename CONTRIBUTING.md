# Contributing to mkv-api-client

Thanks for your interest! This guide covers the most common contribution workflows.

## Setup

```bash
git clone https://github.com/Hochfrequenz/mkv-api-client.git
cd mkv-api-client

# Python
pip install -e ".[tests,linting,type_check,formatting,spell_check]"

# Go
go mod download
```

## Before opening a PR

Run locally:

```bash
# Python
tox -e tests linting type_check coverage spell_check
black . && isort .

# Go
go test ./mcm/...
golangci-lint run --enable dupl,goconst,gocyclo
```

CI also checks these — but running locally is faster.

## Updating from new spec versions

When SAP releases a new version of the OpenAPI specs:

1. Download the new specs from [api.sap.com](https://api.sap.com/package/SAPCloudForUtilitiesFoundation/overview) into `specs/`.
2. Diff the old and new specs to find added/removed/changed fields.
3. Update the corresponding Pydantic models in `src/sap_mcm_client/types_*.py` and Go structs in `*.go` at the repo root.
4. Update or add enum values in `src/sap_mcm_client/enums.py` and `enums.go`.
5. Update `specs/ANALYSIS.md` if the overall API shape changed.
6. Add an entry to `CHANGELOG.md` under `[Unreleased]`.
7. Bump the spec version reference in `README.md` limitations section.

Both languages MUST stay in sync. A single PR updating both is preferred.

## Recording live responses

When you have access to a real SAP system:

1. Copy `.env.example` to `.env` and fill in your SAP BTP service binding values.
2. Install the two script dependencies: `pip install httpx python-dotenv`.
3. Run `python scripts/record_responses.py`.
4. Commit the new JSON files under `testdata/recorded/`.
5. Diff against the existing spec-derived fixtures in `testdata/` to spot discrepancies between the spec and the real API.

Recorded responses are committed (they're business data, not secrets). Only `.env` is gitignored.

## Adding a new Pydantic model

1. Add the class to the appropriate `types_*.py` file.
2. Inherit from `MCMBaseModel` (response) or `MCMRequestModel` (request/update DTO).
3. Every field MUST have `Field(description="...")` with text from the OpenAPI spec.
4. Preserve `max_length` constraints from the spec.
5. Use `Decimal` for loss factors, coordinates, power values (IEEE754Compatible mode).
6. Use `UUID` for uuid-format fields, `date` / `datetime` for date types.
7. Add the class to `src/sap_mcm_client/__init__.py` exports and `__all__`.

## Adding a new Go struct

1. Add the struct to the appropriate `*.go` file under `mcm/`.
2. Use pointer types (`*string`, `*int`, `*bool`) for nullable fields, non-pointer for required fields.
3. JSON tags must exactly match the OData wire format (camelCase with `_code` / `_id` suffixes).
4. Use `*Decimal` for decimal fields, `*time.Time` for datetime, `*string` for date-only.
5. Add doc comments derived from the spec for every exported field.
6. Add `omitempty` to all optional field tags.

## Commit messages

Use conventional commits where appropriate:

- `feat: ...` — new feature
- `fix: ...` — bug fix
- `docs: ...` — documentation only
- `test: ...` — test changes only
- `chore: ...` — tooling, dependencies, etc.
- `refactor: ...` — code change without behavior change

## Code quality bar

- **Python:** pylint 10.00/10, mypy `--strict` clean, black + isort formatted, codespell clean.
- **Go:** `go vet` clean, `golangci-lint` clean with `dupl,goconst,gocyclo` enabled.
- **Coverage:** Python ≥ 80%, Go ≥ 80% (enforced in CI).

All PRs must pass CI before merge.

## Conventions

See [CLAUDE.md](CLAUDE.md) for design decisions and key conventions.
