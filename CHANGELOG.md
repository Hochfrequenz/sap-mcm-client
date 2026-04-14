# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial dual-language (Python + Go) client for the SAP Cloud for Utilities Foundation MCM OData V4 APIs.
- Python package `sap-mcm-client` with Pydantic v2 typed models.
- Go module `github.com/Hochfrequenz/mkv-api-client` with clean typed structs.
- Full coverage of the **Measurement Concept Instance** API: list, get, create, update, 7 lifecycle actions (`init_change`, `init_merge`, `init_shutdown`, `init_version_cancel`, `notify_device_removed`, `notify_market_location_removed`, `notify_final_data_entry_ready`), and 5 sub-entity updates.
- Read-only coverage of the **Measurement Concept Class** and **Measurement Concept Model** APIs.
- OAuth2 Client Credentials authentication with automatic token refresh (30 s buffer) and thread-safe caching.
- Custom alias generator (`_to_odata_camel`) that preserves SAP's `_code` / `_id` / `PD` naming conventions.
- Custom Go `Decimal` type supporting IEEE754Compatible JSON (string or number).
- Typed exception hierarchy (Python) / error helpers `IsNotFound`, `IsForbidden`, `IsUnauthorized` (Go).
- 311 tests across both languages (191 Python + 120 Go), CI covering Python 3.11-3.14 and Go 1.25-1.26.
- Shared JSON fixtures in `testdata/` derived from OpenAPI spec examples.

### Known limitations
- Not yet validated against a live SAP system.
- No `$batch` support.
- No Time Series API (planned for v0.2).
- No Instance Migration API (planned for v0.2).
- Enum values may be incomplete — the specs list known codes, but the real system may accept additional values.
