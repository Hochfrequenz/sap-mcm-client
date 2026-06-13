package mcm

import "time"

// MigrationAddress represents an object address of a migrated measurement
// concept instance, corresponding to the OData type MIGObjectAddresses.
type MigrationAddress struct {
	// ID is the universally unique identifier (UUID) of the object address.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	// This foreign key is required (EDMX Nullable="false"), so it is a non-pointer string.
	MeasurementConceptInstanceID string `json:"measurementConceptInstance_id"`
	// CountryCode is the code representing the country/region in which the measurement concept is instantiated.
	CountryCode *string `json:"country_code,omitempty"`
	// CityID is the city ID for which the measurement concept is instantiated.
	CityID *string `json:"cityID,omitempty"`
	// CityName is the name of the city for which the measurement concept is instantiated.
	CityName *string `json:"cityName,omitempty"`
	// CityDistrict is the city district in which the address object resides.
	CityDistrict *string `json:"cityDistrict,omitempty"`
	// PostalCode is the postal code for which the measurement concept is instantiated.
	PostalCode *string `json:"postalCode,omitempty"`
	// StreetID is the street ID for which the measurement concept is instantiated.
	StreetID *string `json:"streetID,omitempty"`
	// StreetName is the name of the street on which the measurement concept is instantiated.
	StreetName *string `json:"streetName,omitempty"`
	// HouseNumber is the number of the premise for which the measurement concept is instantiated.
	HouseNumber *string `json:"houseNumber,omitempty"`
	// HouseNumberSupplement is the number of the supplement of the address object.
	HouseNumberSupplement *string `json:"houseNumberSupplement,omitempty"`
	// FloorNumber is the floor number of the premise for which the measurement concept is instantiated.
	FloorNumber *string `json:"floorNumber,omitempty"`
	// Supplement is the supplement of the address object.
	Supplement *string `json:"supplement,omitempty"`
	// Latitude is the latitude of the address for which the measurement concept is instantiated.
	Latitude *Decimal `json:"latitude,omitempty"`
	// Longitude is the longitude of the address for which the measurement concept is instantiated.
	Longitude *Decimal `json:"longitude,omitempty"`
	// TimeZone is the time zone in which the measurement concept is instantiated.
	TimeZone *string `json:"timeZone,omitempty"`
}

// MigrationMeteringTask represents a metering task attached to a metering
// location during migration, corresponding to the OData type MIGMeteringTasks.
//
// Unlike the Instance-API MeteringTask, the migration variant exposes
// plannedMeteringProcedure_code and plannedRegisterCode alongside the
// determined values for post-installation bookkeeping.
type MigrationMeteringTask struct {
	// ID is the universally unique identifier (UUID) of the metering task.
	ID string `json:"id"`
	// MeteringLocationID is the universally unique identifier (UUID) of the metering location.
	// This foreign key is required (EDMX Nullable="false"), so it is a non-pointer string.
	MeteringLocationID string `json:"meteringLocation_id"`
	// ModelMeteringTasksID is the universally unique identifier (UUID) of the model metering task.
	ModelMeteringTasksID *string `json:"modelMeteringTasks_id,omitempty"`
	// DirectionCode is the code for the direction of the actor.
	DirectionCode *string `json:"direction_code,omitempty"`
	// LossFactorTransformer is the loss factor of the transformer.
	LossFactorTransformer *Decimal `json:"lossFactorTransformer,omitempty"`
	// LossFactorLine is the loss factor of the line.
	LossFactorLine *Decimal `json:"lossFactorLine,omitempty"`
	// TypeCode is the code representing the type of metering task.
	TypeCode *string `json:"type_code,omitempty"`
	// Position is the position of the metering task.
	Position *int `json:"position,omitempty"`
	// PlannedMeteringProcedureCode is the planned metering procedure code.
	PlannedMeteringProcedureCode *string `json:"plannedMeteringProcedure_code,omitempty"`
	// PlannedRegisterCode is the OBIS-based register code that is planned before the installation of devices.
	PlannedRegisterCode *string `json:"plannedRegisterCode,omitempty"`
	// RegisterCode is the OBIS-based register code that is determined after the installation of devices.
	RegisterCode *string `json:"registerCode,omitempty"`
}

// MigrationMarketLocationUsage represents a market location usage entry on
// a migration calculation rule, corresponding to the OData type
// MIGMarketLocationUsages.
type MigrationMarketLocationUsage struct {
	// ID is the universally unique identifier (UUID) of the market location usage.
	ID string `json:"id"`
	// CalculationRuleID is the universally unique identifier (UUID) of the calculation rule.
	CalculationRuleID *string `json:"calculationRule_id,omitempty"`
	// UsageCode is the code representing the usage of the market location.
	UsageCode *string `json:"usage_code,omitempty"`
	// Position is the position of the market location usage.
	Position *int `json:"position,omitempty"`
}

// MigrationCalculationRule represents a calculation rule of a migrated
// market location, corresponding to the OData type MIGCalculationRules.
//
// The migration variant omits the expressionExpanded and steps fields that
// appear on the Instance-API CalculationRule.
type MigrationCalculationRule struct {
	// ID is the universally unique identifier (UUID) of the calculation rule.
	ID string `json:"id"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID *string `json:"marketLocation_id,omitempty"`
	// ModelCalculationRuleID is the universally unique identifier (UUID) of the model calculation rule.
	ModelCalculationRuleID *string `json:"modelCalculationRule_id,omitempty"`
	// MeteringProcedureCode is the code representing the metering procedure of a metering task.
	MeteringProcedureCode *string `json:"meteringProcedure_code,omitempty"`
	// Expression is the condensed formula that expresses unsuppressed loss factors in a human-readable format.
	Expression *string `json:"expression,omitempty"`
	// PlannedRegisterCode is the OBIS-based register code that is planned before the installation of devices.
	PlannedRegisterCode *string `json:"plannedRegisterCode,omitempty"`
	// RegisterCode is the OBIS-based register code that is determined after the installation of devices.
	RegisterCode *string `json:"registerCode,omitempty"`
	// Position is the position of the calculation rule.
	Position *int `json:"position,omitempty"`
	// Usages is the list of usages for this calculation rule.
	Usages []MigrationMarketLocationUsage `json:"usages,omitempty"`
}

// MigrationMarketLocationActor represents a link between an actor and a
// market location in migration payloads, corresponding to the OData type
// MIGMarketLocationActors.
type MigrationMarketLocationActor struct {
	// ID is the universally unique identifier (UUID) of the market location actor mapping.
	ID string `json:"id"`
	// ActorID is the universally unique identifier (UUID) of the actor.
	ActorID *string `json:"actor_id,omitempty"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID *string `json:"marketLocation_id,omitempty"`
	// Position is the position of the market location actor mapping.
	Position *int `json:"position,omitempty"`
}

// MigrationMeteringLocation represents a metering location of a migrated
// measurement concept instance, corresponding to the OData type
// MIGMeteringLocations.
//
// Unlike the Instance-API MeteringLocation, the migration variant exposes
// the altitude field and omits disconnectable, locationInstalled,
// locationRemoved, and removalDate. IDText is required and up to 60
// characters long.
type MigrationMeteringLocation struct {
	// ID is the universally unique identifier (UUID) of the metering location.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID *string `json:"measurementConceptInstance_id,omitempty"`
	// ModelMeteringLocationID is the universally unique identifier (UUID) of the model metering location.
	ModelMeteringLocationID *string `json:"modelMeteringLocation_id,omitempty"`
	// IDText is the text describing the universally unique identifier (UUID) of the metering location.
	IDText string `json:"idText"`
	// TypeCode is the code representing the type of metering location.
	TypeCode *string `json:"type_code,omitempty"`
	// Position is the position of the metering location.
	Position *int `json:"position,omitempty"`
	// MeteringLocationID is the ID of the metering location.
	MeteringLocationID *string `json:"meteringLocationId,omitempty"`
	// GridCode is the code representing the grid of the metering location.
	GridCode *string `json:"grid_code,omitempty"`
	// Altitude is the altitude of the metering location.
	Altitude *Decimal `json:"altitude,omitempty"`
	// GridLevelCode is the code representing the grid level of the metering location.
	GridLevelCode *string `json:"gridLevel_code,omitempty"`
	// AddressID is the universally unique identifier (UUID) of the address to which the metering location is assigned.
	AddressID *string `json:"address_id,omitempty"`
	// LossTransformerDemand is the transformer loss in the Demand direction.
	LossTransformerDemand *Decimal `json:"lossTransformerDemand,omitempty"`
	// LossLineDemand is the line loss in the Demand direction.
	LossLineDemand *Decimal `json:"lossLineDemand,omitempty"`
	// LossTransformerSupply is the transformer loss in the Supply direction.
	LossTransformerSupply *Decimal `json:"lossTransformerSupply,omitempty"`
	// LossLineSupply is the line loss in the Supply direction.
	LossLineSupply *Decimal `json:"lossLineSupply,omitempty"`
	// MeteringLocationPurposeCode is the code of the metering location purpose.
	MeteringLocationPurposeCode *string `json:"meteringLocationPurpose_code,omitempty"`
	// TransformerRequired indicates whether a transformer is required.
	TransformerRequired *bool `json:"transformerRequired,omitempty"`
	// DeviceSerialID is the universally unique identifier (UUID) of the device.
	DeviceSerialID *string `json:"deviceSerialId,omitempty"`
	// InstallationDate is the date on which the metering location is installed.
	InstallationDate *string `json:"installationDate,omitempty"`
	// MeteringTasks is the list of metering tasks for this metering location.
	MeteringTasks []MigrationMeteringTask `json:"meteringTasks,omitempty"`
}

// MigrationMarketLocation represents a market location of a migrated
// measurement concept instance, corresponding to the OData type
// MIGMarketLocations.
//
// Unlike the Instance-API MarketLocation, the migration variant omits the
// removalDate, locationRemoved, and locationComplete fields. IDText is
// required and up to 60 characters long.
type MigrationMarketLocation struct {
	// ID is the universally unique identifier (UUID) of the market location.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID *string `json:"measurementConceptInstance_id,omitempty"`
	// ModelMarketLocationID is the universally unique identifier (UUID) of the model market location.
	ModelMarketLocationID *string `json:"modelMarketLocation_id,omitempty"`
	// IDText is the text describing the universally unique identifier (UUID) of the market location.
	IDText string `json:"idText"`
	// TypeCode is the code representing the type of market location.
	TypeCode *string `json:"type_code,omitempty"`
	// DirectionCode is the code for the direction of the actor.
	DirectionCode *string `json:"direction_code,omitempty"`
	// Position is the position of the market location.
	Position *int `json:"position,omitempty"`
	// MarketLocationID is the ID of the market location.
	MarketLocationID *string `json:"marketLocationId,omitempty"`
	// AddressID is the universally unique identifier (UUID) of the address to which the market location is assigned.
	AddressID *string `json:"address_id,omitempty"`
	// CommercialSetupDate is the date on which the setup activities for billing, settlement, and other commercial data processing are completed.
	CommercialSetupDate *string `json:"commercialSetupDate,omitempty"`
	// VirtualMarketLocation indicates whether the market location is virtual.
	VirtualMarketLocation *bool `json:"virtualMarketLocation,omitempty"`
	// BillingProcedure is the metering procedure that is used for calculating the billing procedure.
	BillingProcedure *string `json:"billingProcedure,omitempty"`
	// SettlementProcedure is the metering procedure that is used for calculating the settlement procedure.
	SettlementProcedure *string `json:"settlementProcedure,omitempty"`
	// CalculationRules is the list of calculation rules for this market location.
	CalculationRules []MigrationCalculationRule `json:"calculationRules,omitempty"`
	// ActorsMapping is the list of actor mappings for this market location.
	ActorsMapping []MigrationMarketLocationActor `json:"actorsMapping,omitempty"`
}

// MigrationActor represents an actor of a migrated measurement concept
// instance, corresponding to the OData type MIGActors.
//
// The migration variant adds subType_code, interruptible_code,
// externalActorId, installationDate, and commercialSetupDate compared to
// the Instance-API Actor. IDText is required and up to 60 characters long.
type MigrationActor struct {
	// ID is the universally unique identifier (UUID) of the actor.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID *string `json:"measurementConceptInstance_id,omitempty"`
	// ModelActorID is the universally unique identifier (UUID) of the model actor.
	ModelActorID *string `json:"modelActor_id,omitempty"`
	// IDText is the text describing the universally unique identifier (UUID) of the actor.
	IDText string `json:"idText"`
	// TypeCode is the code representing the type of actor.
	TypeCode *string `json:"type_code,omitempty"`
	// DirectionCode is the code for the direction of the actor.
	DirectionCode *string `json:"direction_code,omitempty"`
	// PowerRangeCode is the code representing the power range of an actor.
	PowerRangeCode *string `json:"powerRange_code,omitempty"`
	// Position is the position of the actor.
	Position *int `json:"position,omitempty"`
	// EnergySourceCode is the code representing the energy source of an actor.
	EnergySourceCode *string `json:"energySource_code,omitempty"`
	// SubTypeCode is the subtype of an actor.
	SubTypeCode *string `json:"subType_code,omitempty"`
	// AddressID is the universally unique identifier (UUID) of the address to which the actor is assigned.
	AddressID *string `json:"address_id,omitempty"`
	// GridLevelCode is the code representing the grid level of the actor.
	GridLevelCode *string `json:"gridLevel_code,omitempty"`
	// IsOwnConsumption indicates whether the purpose of the metering location is for self-consumption.
	IsOwnConsumption *bool `json:"isOwnConsumption,omitempty"`
	// InstallationDate is the date on which the actor is installed.
	InstallationDate *string `json:"installationDate,omitempty"`
	// CommercialSetupDate is the date on which the setup activities for billing, settlement, and other commercial data processing are completed.
	CommercialSetupDate *string `json:"commercialSetupDate,omitempty"`
	// InterruptibleCode is the code that indicates whether and how the actor can be interrupted.
	InterruptibleCode *string `json:"interruptible_code,omitempty"`
	// ExternalActorID is the external ID of the actor, used to reference the actor in legacy systems.
	ExternalActorID *string `json:"externalActorId,omitempty"`
	// MarketLocations is the list of market location mappings for this actor.
	MarketLocations []MigrationMarketLocationActor `json:"marketLocations,omitempty"`
}

// MigrationOperandMapping represents an operand-to-metering-task mapping
// for a migrated instance, corresponding to the OData type
// MIGOperandMappings.
type MigrationOperandMapping struct {
	// ID is the universally unique identifier (UUID) of the operand mapping.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID *string `json:"measurementConceptInstance_id,omitempty"`
	// Operand is the variables of a formula that are mapped to metering tasks.
	Operand *string `json:"operand,omitempty"`
	// Value is the literal value assigned to a repeatable operand mapping.
	Value *string `json:"value,omitempty"`
	// MeteringTaskID is the universally unique identifier (UUID) of the metering task.
	MeteringTaskID *string `json:"meteringTask_id,omitempty"`
	// Position is the position of the operand mapping.
	Position *int `json:"position,omitempty"`
}

// MigrationChangeProcess represents a change process for a migrated
// measurement concept instance, corresponding to the OData type
// MIGChangeProcesses.
//
// Unlike the Instance-API ChangeProcess, the migration variant does not
// carry embedded processData or instanceCharacteristics.
type MigrationChangeProcess struct {
	// ID is the universally unique identifier (UUID) of the change process.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID *string `json:"measurementConceptInstance_id,omitempty"`
	// ExternalOrderID is the ID of the external order that corresponds to the instantiation of the measurement concept.
	ExternalOrderID *string `json:"externalOrderId,omitempty"`
	// ExternalProcessID is the reference to the process ID from the pre-system.
	ExternalProcessID *string `json:"externalProcessId,omitempty"`
	// ProcessTypeCode is the code of the process type that is involved in the change process.
	ProcessTypeCode *string `json:"processType_code,omitempty"`
	// StatusID is the universally unique identifier (UUID) of the status of the change process.
	StatusID *string `json:"status_id,omitempty"`
	// Finished indicates whether the change process is finished.
	Finished *bool `json:"finished,omitempty"`
	// ModifiedAt is the date and time at which the change process was last modified.
	ModifiedAt *time.Time `json:"modifiedAt,omitempty"`
}

// MigrationStatus represents the combined instance- and process-status of
// a migrated measurement concept instance, corresponding to the OData
// type MIGStatus.
type MigrationStatus struct {
	// ID is the universally unique identifier (UUID) of the status.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID *string `json:"measurementConceptInstance_id,omitempty"`
	// ChangeProcessID is the universally unique identifier (UUID) of the change process.
	ChangeProcessID *string `json:"changeProcess_id,omitempty"`
	// InstanceStatusCode is the status code of the measurement concept instance.
	InstanceStatusCode *string `json:"instanceStatus_code,omitempty"`
	// ProcessStatusCode is the process status code of the measurement concept instance.
	ProcessStatusCode *string `json:"processStatus_code,omitempty"`
}

// MigrationInstance represents a single measurement concept instance to be
// submitted through the POST /migrate endpoint. Corresponds to the
// mcmInstances.MigrationInstances-migrate schema
// (InputMigrationInstances in the EDMX metadata).
type MigrationInstance struct {
	// ID is the universally unique identifier (UUID) of the measurement concept instance.
	ID string `json:"id"`
	// IDText is the human-readable identifier of the measurement concept instance.
	IDText string `json:"idText"`
	// Version is the version of the measurement concept instance.
	Version *string `json:"version,omitempty"`
	// MeasurementModelID is the universally unique identifier (UUID) of the measurement concept model from which the measurement concept is instantiated.
	MeasurementModelID *string `json:"measurementModel_id,omitempty"`
	// MeasurementClassID is the universally unique identifier (UUID) of the measurement concept class that is referenced by the measurement concept instance.
	MeasurementClassID *string `json:"measurementClass_id,omitempty"`
	// LeadingGridCode is the code representing the leading grid of the measurement concept instance.
	LeadingGridCode *string `json:"leadingGrid_code,omitempty"`
	// Description is the description of the measurement concept instance.
	Description *string `json:"description,omitempty"`
	// OrdererCode is the code representing the orderer of the measurement concept instance.
	OrdererCode *string `json:"orderer_code,omitempty"`
	// DivisionCode is the code representing the division of the measurement concept instance.
	DivisionCode *string `json:"division_code,omitempty"`
	// LeadingAddressID is the universally unique identifier (UUID) of the leading address of the measurement concept instance.
	LeadingAddressID *string `json:"leadingAddress_id,omitempty"`
	// InstalledOn is the date on which the physical installation processes are completed.
	InstalledOn *string `json:"installedOn,omitempty"`
	// InstalledUntil is the date until a version of a measurement concept instance is valid.
	InstalledUntil *string `json:"installedUntil,omitempty"`
	// CommercialSetupOn is the date on which the commercial setup processes are completed.
	CommercialSetupOn *string `json:"commercialSetupOn,omitempty"`
	// Overwrite controls whether an existing instance with the same ID is overwritten during migration.
	Overwrite *bool `json:"overwrite,omitempty"`
	// Addresses is the list of addresses for the migrated instance.
	Addresses []MigrationAddress `json:"addresses,omitempty"`
	// ChangeProcesses is the list of change processes for the migrated instance.
	ChangeProcesses []MigrationChangeProcess `json:"changeProcesses,omitempty"`
	// MeteringLocations is the list of metering locations for the migrated instance.
	MeteringLocations []MigrationMeteringLocation `json:"meteringLocations,omitempty"`
	// MarketLocations is the list of market locations for the migrated instance.
	MarketLocations []MigrationMarketLocation `json:"marketLocations,omitempty"`
	// Actors is the list of actors for the migrated instance.
	Actors []MigrationActor `json:"actors,omitempty"`
	// OperandMappings is the list of operand mappings for the migrated instance.
	OperandMappings []MigrationOperandMapping `json:"operandMappings,omitempty"`
}

// MigrationInstancesRequest is the request-body wrapper for the
// POST /migrate endpoint.
type MigrationInstancesRequest struct {
	// MigrationInstances is the list of measurement concept instances to migrate.
	MigrationInstances []MigrationInstance `json:"migrationInstances"`
}

// MigrationResponse is the response body of the POST /migrate endpoint.
type MigrationResponse struct {
	// RequestID is the universally unique identifier (UUID) of the migration request.
	// Use it to query the status of the staged migration instances.
	RequestID string `json:"requestId"`
}

// MigrationInstanceResponse represents a measurement concept instance as
// returned by GET /MigrationInstances({id}). Corresponds to the
// mcmInstances.MigrationInstance-Response schema (MigrationInstances in
// the EDMX metadata).
type MigrationInstanceResponse struct {
	// ID is the universally unique identifier (UUID) of the measurement concept instance.
	ID string `json:"id"`
	// IDText is the human-readable identifier of the measurement concept instance.
	IDText string `json:"idText"`
	// Version is the version of the measurement concept instance.
	Version *string `json:"version,omitempty"`
	// MeasurementModelID is the universally unique identifier (UUID) of the measurement concept model from which the measurement concept is instantiated.
	MeasurementModelID *string `json:"measurementModel_id,omitempty"`
	// MeasurementClassID is the universally unique identifier (UUID) of the measurement concept class referenced by the measurement concept instance.
	MeasurementClassID *string `json:"measurementClass_id,omitempty"`
	// LeadingGridCode is the code representing the leading grid of the measurement concept instance.
	LeadingGridCode *string `json:"leadingGrid_code,omitempty"`
	// Description is the description of the measurement concept instance.
	Description *string `json:"description,omitempty"`
	// OrdererCode is the code representing the orderer of the measurement concept instance.
	OrdererCode *string `json:"orderer_code,omitempty"`
	// DivisionCode is the code representing the division of the measurement concept instance.
	DivisionCode *string `json:"division_code,omitempty"`
	// LeadingAddressID is the universally unique identifier (UUID) of the leading address of the measurement concept instance.
	LeadingAddressID *string `json:"leadingAddress_id,omitempty"`
	// InstalledOn is the date on which the physical installation processes are completed.
	InstalledOn *string `json:"installedOn,omitempty"`
	// InstalledUntil is the date until a version of a measurement concept instance is valid.
	InstalledUntil *string `json:"installedUntil,omitempty"`
	// CommercialSetupOn is the date on which the commercial setup processes are completed.
	CommercialSetupOn *string `json:"commercialSetupOn,omitempty"`
	// OverallStatusCode is the combined status of the instance status and the process status.
	OverallStatusCode *string `json:"overallStatus_code,omitempty"`
	// StatusID is the universally unique identifier (UUID) of the status of the measurement concept instance.
	StatusID *string `json:"status_id,omitempty"`
	// ModifiedAt is the date and time at which the measurement concept instance was last modified.
	ModifiedAt *time.Time `json:"modifiedAt,omitempty"`
	// Overwrite indicates whether the instance was imported with the overwrite flag set.
	Overwrite *bool `json:"overwrite,omitempty"`
	// Addresses is the list of addresses for this instance.
	Addresses []MigrationAddress `json:"addresses,omitempty"`
	// ChangeProcesses is the list of change processes for this instance.
	ChangeProcesses []MigrationChangeProcess `json:"changeProcesses,omitempty"`
	// MeteringLocations is the list of metering locations for this instance.
	MeteringLocations []MigrationMeteringLocation `json:"meteringLocations,omitempty"`
	// MarketLocations is the list of market locations for this instance.
	MarketLocations []MigrationMarketLocation `json:"marketLocations,omitempty"`
	// Actors is the list of actors for this instance.
	Actors []MigrationActor `json:"actors,omitempty"`
	// OperandMappings is the list of operand mappings for this instance.
	OperandMappings []MigrationOperandMapping `json:"operandMappings,omitempty"`
	// Status is the status of this instance.
	Status *MigrationStatus `json:"status,omitempty"`
}

// StagedMigrationInstance represents a single entry in the
// StagedMigrationInstances collection. Staged entries track the per-instance
// lifecycle of a migrate request (received -> in-progress ->
// succeeded/failed) and carry the raw JSON payload in InstanceData until
// the migration completes.
type StagedMigrationInstance struct {
	// ID is the universally unique identifier (UUID) of the staged migration entry.
	ID string `json:"id"`
	// ModifiedAt is the date and time at which the staged entry was last modified.
	ModifiedAt *time.Time `json:"modifiedAt,omitempty"`
	// CreatedAt is the date and time at which the staged entry was created.
	CreatedAt *time.Time `json:"createdAt,omitempty"`
	// CreatedBy is the user who created the staged entry.
	CreatedBy *string `json:"createdBy,omitempty"`
	// ModifiedBy is the user who last modified the staged entry.
	ModifiedBy *string `json:"modifiedBy,omitempty"`
	// RequestID is the universally unique identifier (UUID) of the migration request that produced this staged entry.
	RequestID *string `json:"requestId,omitempty"`
	// IDText is the human-readable identifier of the staged migration entry.
	IDText string `json:"idText"`
	// InstanceData is the raw JSON representation of the measurement concept instance to migrate.
	InstanceData *string `json:"instanceData,omitempty"`
	// Overwrite indicates whether the staged entry was submitted with the overwrite flag set.
	Overwrite *bool `json:"overwrite,omitempty"`
	// StatusCode is the code for the current migration status of this staged entry.
	StatusCode *string `json:"status_code,omitempty"`
	// StatusReason is the reason for the current migration status of this staged entry.
	StatusReason *string `json:"statusReason,omitempty"`
	// TimeMigrationIn is the date and time at which the staged entry was received for migration.
	TimeMigrationIn *time.Time `json:"timeMigrationIn,omitempty"`
	// TimeMigrationStart is the date and time at which the migration of this staged entry started.
	TimeMigrationStart *time.Time `json:"timeMigrationStart,omitempty"`
	// TimeMigrationEnd is the date and time at which the migration of this staged entry finished.
	TimeMigrationEnd *time.Time `json:"timeMigrationEnd,omitempty"`
	// TimeMigrationDuration is the duration of the migration of this staged entry.
	TimeMigrationDuration *string `json:"timeMigrationDuration,omitempty"`
	// InstanceOverallStatusCode is the overall status of the migrated measurement concept instance.
	InstanceOverallStatusCode *string `json:"instanceOverallStatus_code,omitempty"`
	// InstanceStatusID is the universally unique identifier (UUID) of the status entry of the migrated measurement concept instance.
	InstanceStatusID *string `json:"instanceStatus_id,omitempty"`
	// Instance is the migrated measurement concept instance. Only populated when the request expands "instance".
	Instance *MigrationInstanceResponse `json:"instance,omitempty"`
}

// ProcessProgressStatus is a combined instance- and process-status of a
// migration progress, corresponding to the OData complex type
// MCMMigrationService.ProcessProgressStatus.
type ProcessProgressStatus struct {
	// InstanceStatus is the status code of the measurement concept instance.
	InstanceStatus *string `json:"instanceStatus,omitempty"`
	// ProcessStatus is the process status code of the measurement concept instance.
	ProcessStatus *string `json:"processStatus,omitempty"`
}

// ProcessProgressFailedValidation is a single validation that failed during
// migration, corresponding to the OData complex type
// MCMMigrationService.ProcessProgressFailedValidation.
type ProcessProgressFailedValidation struct {
	// Name is the name of the failed validation.
	Name *string `json:"name,omitempty"`
	// Position is the position associated with the failed validation.
	Position *int `json:"position,omitempty"`
	// Parameters are the parameters associated with the failed validation.
	Parameters []string `json:"parameters,omitempty"`
}

// ProcessProgress is the migration progress of a measurement concept instance
// or change process, returned by the checkProgress function. Corresponds to
// the OData complex type MCMMigrationService.ProcessProgress.
type ProcessProgress struct {
	// ChangeProcessID is the universally unique identifier (UUID) of the change process.
	ChangeProcessID string `json:"changeProcessId"`
	// InstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	InstanceID string `json:"instanceId"`
	// InstanceIDText is the human-readable identifier of the measurement concept instance.
	InstanceIDText string `json:"instanceIdText"`
	// InstanceVersion is the version of the measurement concept instance.
	InstanceVersion string `json:"instanceVersion"`
	// CurrentStatus is the current combined status of the instance or change process.
	CurrentStatus *ProcessProgressStatus `json:"currentStatus,omitempty"`
	// NextStatus is the next combined status of the instance or change process.
	NextStatus *ProcessProgressStatus `json:"nextStatus,omitempty"`
	// FailedValidations are the validations that failed for the instance or change process, if any.
	FailedValidations []ProcessProgressFailedValidation `json:"failedValidations,omitempty"`
}

// PurgeRequest is the request body for the migration purge action. It carries
// the migration request ID whose staged data is to be deleted.
type PurgeRequest struct {
	// RequestID is the universally unique identifier (UUID) of the migration
	// request to purge, as returned by Migrate.
	RequestID string `json:"requestId"`
}
