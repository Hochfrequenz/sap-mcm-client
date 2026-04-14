# Test Fixtures

These JSON fixtures are **derived from the SAP MCM OpenAPI specification examples**
(v1.1.0). The original spec files are SAP IP and not redistributed in this repository
— see [CONTRIBUTING.md](../CONTRIBUTING.md#downloading-the-openapi-specs) for how to
download them locally. The fixtures here were hand-assembled using field names,
example values, and schema structures from these specs:

- Measurement Concept Instance (`mcm-instance.json`, v1.1.0)
- Measurement Concept Class (`mcm-concept-class.json`, v1.1.0)
- Measurement Concept Model (`mcm-concept-model.json`, v1.1.0)
- Measurement Concept Instance Migration (`mcm-instance-migration-v1.1.0.json`, v1.1.0)

**These fixtures were NOT recorded from a live system.** They represent realistic but
synthetic OData v4 responses constructed to match the wire format described in the
specs. UUIDs, dates, and other field values are plausible examples, not real data.

## Conventions

- Field names use the exact OData camelCase wire format with `_code` and `_id`
  suffixes as specified in the schemas.
- Decimal fields (loss factors, coordinates) are encoded as JSON strings to match
  OData IEEE 754 Compatible mode (`Content-Type: application/json;IEEE754Compatible=true`).
- Dates are ISO 8601 strings (`YYYY-MM-DD` for date, full ISO for date-time).
- Collection responses include `@odata.count` and `value` array.
- Single-entity responses include `@context` and `@metadataEtag` OData envelope fields.

## Files

| File | Description |
|---|---|
| `instance_get.json` | Single MCI with all navigation properties expanded |
| `instance_list.json` | Collection of 2 minimal MCI entities |
| `class_get.json` | Single MCC with meteringLocations and actors |
| `class_list.json` | Collection of 2 MCC entities |
| `model_get.json` | Single MCD with marketLocations and modelOperands |
| `model_list.json` | Collection of 2 MCD entities |
| `error_401.json` | OData error response for HTTP 401 Unauthorized |
| `error_403.json` | OData error response for HTTP 403 Forbidden |
| `error_404.json` | OData error response for HTTP 404 Not Found |
