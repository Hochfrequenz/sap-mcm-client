package mcm

// Enum values in this file are derived from the OpenAPI specs (v1.1.0)
// downloaded from api.sap.com on 2026-04-13. The real SAP system may
// accept additional codes not listed here. All enums are typed strings,
// so unknown values from the API will still deserialize correctly.

// Division represents the energy division of a measurement concept.
// The division is derived from the referenced measurement concept model and class.
type Division string

const (
	// DivisionElectricity is the electricity division.
	DivisionElectricity Division = "EL"
	// DivisionGas is the gas division.
	DivisionGas Division = "GA"
	// DivisionWater is the water division.
	DivisionWater Division = "WA"
	// DivisionRemoteHeat is the remote heat division.
	DivisionRemoteHeat Division = "RH"
)

// OverallStatus is the combined status of the instance status and
// the process status of a measurement concept instance.
type OverallStatus string

const (
	// OverallStatusInitial indicates the instance has been created but not yet processed.
	OverallStatusInitial OverallStatus = "INITIAL"
	// OverallStatusNew indicates the instance is new and awaiting processing.
	OverallStatusNew OverallStatus = "NEW"
	// OverallStatusError indicates an error occurred during processing.
	OverallStatusError OverallStatus = "ERROR"
	// OverallStatusActive indicates the instance is active and operational.
	OverallStatusActive OverallStatus = "ACTIVE"
	// OverallStatusHistoric indicates the instance has been superseded by a newer version.
	OverallStatusHistoric OverallStatus = "HISTORIC"
	// OverallStatusVersionCancel indicates the instance version has been cancelled.
	OverallStatusVersionCancel OverallStatus = "VERSION_CANCEL"
)

// ClassType represents the type of a measurement concept class.
// SAP templates are read-only reference templates; CLASS is production-usable.
type ClassType string

const (
	// ClassTypeClass is a production-usable measurement concept class.
	ClassTypeClass ClassType = "CLASS"
	// ClassTypeSAPTemplate is a read-only SAP reference template.
	ClassTypeSAPTemplate ClassType = "SAPTEMPLATE"
)

// ConceptType represents the type of a measurement concept model.
// SAP templates are read-only reference templates; MODEL is production-usable.
type ConceptType string

const (
	// ConceptTypeModel is a production-usable measurement concept model.
	ConceptTypeModel ConceptType = "MODEL"
	// ConceptTypeSAPTemplate is a read-only SAP reference template.
	ConceptTypeSAPTemplate ConceptType = "SAPTEMPLATE"
)

// ModelStatus represents the status of a measurement concept model.
type ModelStatus string

const (
	// ModelStatusInProgress indicates the model is being edited.
	ModelStatusInProgress ModelStatus = "IN_PROGRESS"
	// ModelStatusActive indicates the model is active and can be used for instantiation.
	ModelStatusActive ModelStatus = "ACTIVE"
	// ModelStatusDeactivated indicates the model has been deactivated.
	ModelStatusDeactivated ModelStatus = "DEACTIVATED"
)

// Direction represents the energy flow direction of an actor or market location.
// For electricity, both IN (supply/feed-in) and OUT (demand/consumption) are supported.
// For gas, water, and remote heat, only OUT is supported.
type Direction string

const (
	// DirectionIn is the supply / feed-in direction.
	DirectionIn Direction = "IN"
	// DirectionOut is the demand / consumption direction.
	DirectionOut Direction = "OUT"
)

// ActorType represents the type of an actor in a measurement concept.
type ActorType string

const (
	// ActorTypeConsumer is a consumer of energy.
	ActorTypeConsumer ActorType = "CONSUMER"
	// ActorTypeProducer is a producer / generator of energy.
	ActorTypeProducer ActorType = "PRODUCER"
	// ActorTypeStorage is an energy storage unit.
	ActorTypeStorage ActorType = "STORAGE"
)

// MeteringLocationType represents the type of a metering location
// within a measurement concept class.
type MeteringLocationType string

const (
	// MeteringLocationTypeGridMes is a grid measurement point.
	MeteringLocationTypeGridMes MeteringLocationType = "GRIDMES"
	// MeteringLocationTypeSeriesMes is a serial switching measurement point.
	MeteringLocationTypeSeriesMes MeteringLocationType = "SERIESMES"
	// MeteringLocationTypeGeneratorMes is a generator measurement point.
	MeteringLocationTypeGeneratorMes MeteringLocationType = "GENERATORMES"
	// MeteringLocationTypeStorageMes is a storage measurement point.
	MeteringLocationTypeStorageMes MeteringLocationType = "STORAGEMES"
	// MeteringLocationTypeDiffMes is a difference measurement point.
	MeteringLocationTypeDiffMes MeteringLocationType = "DIFFMES"
	// MeteringLocationTypeCompareMes is a comparative measurement point.
	MeteringLocationTypeCompareMes MeteringLocationType = "COMPAREMES"
)

// MeteringTaskType represents the type of a metering task assigned to a metering location.
type MeteringTaskType string

const (
	// MeteringTaskTypeAE is active energy measurement (Arbeitsenergieerfassung).
	MeteringTaskTypeAE MeteringTaskType = "AE"
	// MeteringTaskTypeOV is operating volume measurement (Betriebsvolumen).
	MeteringTaskTypeOV MeteringTaskType = "OV"
	// MeteringTaskTypeEV is energetic value measurement (Energetischer Wert).
	MeteringTaskTypeEV MeteringTaskType = "EV"
)

// MeteringProcedure represents the metering procedure of a metering task.
// Determines how meter readings are collected and processed.
type MeteringProcedure string

const (
	// MeteringProcedureSLP is standard load profile (Standardlastprofil).
	MeteringProcedureSLP MeteringProcedure = "SLP"
	// MeteringProcedureRLM is interval reading (registrierende Leistungsmessung).
	MeteringProcedureRLM MeteringProcedure = "RLM"
	// MeteringProcedureIR is interval recording.
	MeteringProcedureIR MeteringProcedure = "IR"
)

// MarketLocationUsage represents the usage purpose of a market location calculation rule.
type MarketLocationUsage string

const (
	// MarketLocationUsageBilling is used for billing.
	MarketLocationUsageBilling MarketLocationUsage = "BILLING"
	// MarketLocationUsageGridUse is used for grid usage calculation.
	MarketLocationUsageGridUse MarketLocationUsage = "GRIDUSE"
	// MarketLocationUsageOUBill is used for own-use billing.
	MarketLocationUsageOUBill MarketLocationUsage = "OUBILL"
	// MarketLocationUsageREB is used for rebilling.
	MarketLocationUsageREB MarketLocationUsage = "REB"
	// MarketLocationUsageSettle is used for settlement.
	MarketLocationUsageSettle MarketLocationUsage = "SETTLE"
)

// MarketLocationType represents the type of a market location.
type MarketLocationType string

const (
	// MarketLocationTypeSupply is a supply market location.
	MarketLocationTypeSupply MarketLocationType = "SUPPLY"
)

// ProcessType represents the type of a change process for a measurement concept instance.
type ProcessType string

const (
	// ProcessTypeCreate is the initial creation of the instance.
	ProcessTypeCreate ProcessType = "CREATE"
)

// MeteringLocationPurpose represents the purpose of a metering location
// in a measurement concept model.
type MeteringLocationPurpose string

const (
	// MeteringLocationPurposeSC is self-consumption (Eigenverbrauch).
	MeteringLocationPurposeSC MeteringLocationPurpose = "SC"
	// MeteringLocationPurposeCST is commercial settlement transfer.
	MeteringLocationPurposeCST MeteringLocationPurpose = "CST"
)

// ForecastBasis represents the forecast basis of a market location.
type ForecastBasis string

const (
	// ForecastBasisRLM is interval reading based forecast.
	ForecastBasisRLM ForecastBasis = "RLM"
	// ForecastBasisREM is remainder based forecast.
	ForecastBasisREM ForecastBasis = "REM"
	// ForecastBasisHO is household based forecast.
	ForecastBasisHO ForecastBasis = "HO"
)

// MeasuringType represents the measuring type of a metering location in process data.
type MeasuringType string

const (
	// MeasuringTypeCME is conventional metering equipment.
	MeasuringTypeCME MeasuringType = "CME"
	// MeasuringTypeMME is modern metering equipment (smart meter).
	MeasuringTypeMME MeasuringType = "MME"
)

// Rate represents the tariff rate code of a metering task.
type Rate string

const (
	// RateSingleRate is a single rate tariff (Eintarif).
	RateSingleRate Rate = "SR"
	// RateDoubleRate is a double rate tariff (Doppeltarif).
	RateDoubleRate Rate = "DR"
)
