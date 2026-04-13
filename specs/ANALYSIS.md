# MKV API Analysis

## Known APIs

### 1. MCM Instance Migration API (spec available)
- **Spec:** `mcm-instance-migration-v1.1.0.json`
- **Base:** `https://c4u-foundation-mcm-service.cfapps.{region}.hana.ondemand.com`
- **Path:** `/odata/v4/api/migrate/v1/`
- **Operations:** POST migrate, GET MigrationInstances({id}), GET StagedMigrationInstances
- **Auth:** OAuth2 Client Credentials
- **Regions:** eu10, ap10

### 2. MCM Instance CRUD API (inferred from batch example)
- **Spec:** TODO — download from api.sap.com
- **Path:** `/odata/v4/api/mcm/v1/`
- **EntitySets:** MCMInstances (+ navigation to sub-entities)
- **Operations:** PATCH confirmed, likely full CRUD
- **Batch:** `$batch` endpoint, multipart/mixed

### 3. MCM Concept Class API (known to exist)
- **Spec:** TODO — download from api.sap.com
- **api.sap.com name:** MCMConceptClass

### 4. MCM Concept Model API (known to exist)
- **Spec:** TODO — download from api.sap.com

## Entity Hierarchy

```
MeasurementConceptInstance
├── meteringLocations[]              # Messstellen
│   └── meteringTasks[]              # Messaufgaben (OBIS codes, loss factors)
├── marketLocations[]                # Marktlokationen (MaLo)
│   └── calculationRules[]           # Berechnungsregeln
│       └── usages[]                 # Verwendungszwecke
├── actors[]                         # Akteure (Consumer/Producer/Storage)
├── addresses[]                      # Geo + postal addresses
├── changeProcesses[]                # Lifecycle processes
│   └── processData.actorsPD[]       # Process data with external refs
├── operandMappings[]                # Formula operands → metering tasks
└── status                           # Instance + process status
```

## Known Domain Codes

| Domain | Codes |
|---|---|
| division | EL (electricity), GA (gas), WA (water), RH (remote heat) |
| actor type | CONSUMER, PRODUCER, STORAGE |
| direction | IN, OUT |
| metering procedure | SLP (standard load profile), RLM (interval reading) |
| overall status | INITIAL, NEW, ERROR, ACTIVE, HISTORIC |
| process type | CREATE |
| metering location type | GRIDMES |
| market location type | SUPPLY |
| usage | GRIDUSE |

## OData V4 Conventions (observed)

- `Accept: application/json;odata.metadata=minimal;IEEE754Compatible=true`
- Decimals as strings (IEEE754Compatible)
- Nested $expand: `marketLocations($expand=calculationRules($expand=usages),actors)`
- Batch via multipart/mixed
- Navigation property addressing: `MCMInstances({id})/meteringLocations({id})`
- Response metadata: `@context`, `@metadataEtag`

## Client Design Goals

- Universal client, not a 1:1 API mirror
- Hide OData complexity behind typed domain objects
- Fluent query builder for $filter, $expand, $select, $top, $skip
- Transparent OAuth2 + IEEE754 handling
- Batch support for atomic multi-entity updates
- Dual language: Python + Go
- Test via recorded fixtures (VCR pattern), no live SAP needed
