# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

### Added
- **Time Series API** — full client coverage of all 17 endpoints of the SAP Cloud for Utilities Foundation Time Series service.
  - 12 OData V4 read functions under `/odata/v4/api/v1/TimeSeries`, dispatched from `TimeSeriesResource.get_data` / `.get_history` (Python) and `TimeSeriesService.GetByTimeSeriesID` / `.GetByExternalID` / `.GetHistoryBy*` (Go), with automatic base / `Since` / `InPeriod` variant selection.
  - Single-quote literal escaping for UUID, external ID, and `YYYY-MM-DD` query parameters per the OData V4 string literal rule.
  - 2 REST multipart upload endpoints (`/uploadsc` filename-based and `/upload?uploadID=...`).
  - 3 REST delete endpoints (by UUID, by external ID, and bulk via POST body) with spec-derived guard rails (bulk requires at least one UUID or external ID).
  - Unified `TimeSeriesDataPoint` type covering both current-data and historical-value schemas, with `Decimal` value support and nullable missing-value handling.
  - `DeleteTimeSeriesRequest` validation model.
- **Measurement Concept Instance Migration API** — client coverage of all 3 endpoints of the Migration service.
  - `MigrationResource.migrate` (Python) / `MigrationService.Migrate` (Go) wraps a list of `MigrationInstance`s in the required `{"migrationInstances": [...]}` body and returns the `requestId`.
  - `MigrationResource.get` / `MigrationService.Get` builds the full default `$expand` (change processes, status, metering locations + tasks, actors, market locations with calculation rules + usages + actors, addresses, operand mappings).
  - `MigrationResource.list_staged` / `MigrationService.ListStaged` surfaces `$filter=requestId eq <guid>` and `$filter=status_code eq '<status>'` together with `$top`, `$count`, and `$expand=instance`.
  - Migration-specific types: `MigrationInstance`, `MigrationInstanceResponse`, `StagedMigrationInstance`, `MigrationResponse`, and the full `MIG*` sub-entity set — with the migration-only fields the API adds over the Instance API (`idText` up to 60 chars, `altitude`, `subType_code`, `interruptible_code`, `externalActorId`, `plannedMeteringProcedure_code`, `plannedRegisterCode`, `installationDate`, `commercialSetupDate`).
- `scripts/record_responses.py` — live-tenant recorder for creating golden-response fixtures in `testdata/recorded/`, driven by `.env.example`.
- Shared JSON fixtures `testdata/timeseries_data.json`, `testdata/migration_response.json`, `testdata/migration_instance_get.json`, `testdata/migration_staged_list.json` derived from the OpenAPI specs and EDMX metadata for v0.2.
- 47 explicit Pydantic `Field(alias=...)` overrides for non-FK `Id` / `Code` fields (external IDs, OBIS register codes, uppercase address fields, PD ids). The `_to_odata_camel` generator was silently dropping these fields via `extra="ignore"` against real-API responses.
- `unittests/test_alias_consistency.py` — regression test that parses every `json:"..."` tag from `mcm/*.go` and asserts every Pydantic wire name is known to the Go side.
- 93 new tests (58 Python + 35 Go), bringing the total to **419 tests** (249 Python + 170 Go) across both languages.

## [0.1.0]

### Added
- Initial dual-language (Python + Go) client for the SAP Cloud for Utilities Foundation MCM OData V4 APIs.
- Python package `sap-mcm-client` with Pydantic v2 typed models.
- Go module `github.com/Hochfrequenz/sap-mcm-client` with clean typed structs.
- Full coverage of the **Measurement Concept Instance** API: list, get, create, update, 7 lifecycle actions (`init_change`, `init_merge`, `init_shutdown`, `init_version_cancel`, `notify_device_removed`, `notify_market_location_removed`, `notify_final_data_entry_ready`), and 5 sub-entity updates.
- Read-only coverage of the **Measurement Concept Class** and **Measurement Concept Model** APIs.
- OAuth2 Client Credentials authentication with automatic token refresh (30 s buffer) and thread-safe caching.
- Custom alias generator (`_to_odata_camel`) that preserves SAP's `_code` / `_id` / `PD` naming conventions.
- Custom Go `Decimal` type supporting IEEE754Compatible JSON (string or number).
- Typed exception hierarchy (Python) / error helpers `IsNotFound`, `IsForbidden`, `IsUnauthorized` (Go).
- 326 tests across both languages (191 Python + 135 Go), CI covering Python 3.11-3.14 and Go 1.25-1.26.
- Shared JSON fixtures in `testdata/` derived from OpenAPI spec examples.

### Known limitations
- Not yet validated against a live SAP system.
- No `$batch` support.
- No Time Series API (planned for v0.2).
- No Instance Migration API (planned for v0.2).
- Enum values may be incomplete — the specs list known codes, but the real system may accept additional values.
