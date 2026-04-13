// Package mcm provides a Go client for the SAP Cloud for Utilities Foundation
// Measurement Concept Management (MCM) OData V4 APIs.
//
// All type definitions are derived from the SAP MCM OpenAPI specs (v1.1.0)
// downloaded from api.sap.com. Field names, types, and constraints come from
// the specs, not from observed API behavior. These models have not been
// validated against a live SAP system.
//
// Enum values may be incomplete — the specs list known codes, but the real
// system may accept additional values. All enums are typed strings so that
// unknown values will still deserialize without errors.
//
// Use [NewClient] to create a client, then access resources through the
// typed service fields: [Client.Instances], [Client.Classes], [Client.Models].
package mcm
