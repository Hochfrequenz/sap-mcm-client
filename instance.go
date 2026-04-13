package mcm

import "time"

// MarketLocationUsageEntry represents a usage entry on a calculation rule
// within a measurement concept instance.
type MarketLocationUsageEntry struct {
	// ID is the universally unique identifier (UUID) of the market location usage.
	ID string `json:"id"`
	// CalculationRuleID is the universally unique identifier (UUID) of the calculation rule.
	CalculationRuleID string `json:"calculationRule_id"`
	// UsageCode is the code representing the usage of the market location.
	UsageCode *string `json:"usage_code,omitempty"`
	// Position is the position of the market location usage.
	Position *int `json:"position,omitempty"`
}

// CalculationRuleStep represents a single step in a calculation rule
// of a measurement concept instance.
type CalculationRuleStep struct {
	// CalculationRuleID is the universally unique identifier (UUID) of the calculation rule.
	CalculationRuleID string `json:"calculationRule_id"`
	// Step is the step number in the calculation rule.
	Step int `json:"step"`
	// Type is the type of the calculation rule step.
	Type *string `json:"type,omitempty"`
	// Value is the value assigned to this calculation rule step.
	Value *string `json:"value,omitempty"`
	// Ref1 is the first reference of the calculation rule step.
	Ref1 *int `json:"ref1,omitempty"`
	// Ref2 is the second reference of the calculation rule step.
	Ref2 *int `json:"ref2,omitempty"`
	// MeteringTaskID is the universally unique identifier (UUID) of the metering task.
	MeteringTaskID *string `json:"meteringTask_id,omitempty"`
	// MeteringTask is the expanded metering task navigation property.
	MeteringTask *MeteringTask `json:"meteringTask,omitempty"`
}

// CalculationRule represents a calculation rule for a market location
// within a measurement concept instance.
type CalculationRule struct {
	// ID is the universally unique identifier (UUID) of the calculation rule.
	ID string `json:"id"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID string `json:"marketLocation_id"`
	// MeteringProcedureCode is the code representing the metering procedure of a metering task.
	MeteringProcedureCode string `json:"meteringProcedure_code"`
	// ModelCalculationRuleID is the universally unique identifier (UUID) of the model calculation rule.
	ModelCalculationRuleID *string `json:"modelCalculationRule_id,omitempty"`
	// Expression is the condensed formula that expresses unsuppressed loss factors in a human-readable format.
	Expression *string `json:"expression,omitempty"`
	// ExpressionExpanded is the expanded formula, which consists of a general formula that is augmented by loss factors and applied rules.
	ExpressionExpanded *string `json:"expressionExpanded,omitempty"`
	// PlannedRegisterCode is the OBIS-based register code that is planned before the installation of devices.
	PlannedRegisterCode *string `json:"plannedRegisterCode,omitempty"`
	// RegisterCode is the OBIS-based register code that is determined after the installation of devices.
	RegisterCode *string `json:"registerCode,omitempty"`
	// Position is the position of the calculation rule.
	Position *int `json:"position,omitempty"`
	// Steps is the list of steps in this calculation rule.
	Steps []CalculationRuleStep `json:"steps,omitempty"`
	// Usages is the list of usages for this calculation rule.
	Usages []MarketLocationUsageEntry `json:"usages,omitempty"`
}

// MarketLocation represents a market location within a measurement concept instance.
type MarketLocation struct {
	// ID is the universally unique identifier (UUID) of the market location.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID string `json:"measurementConceptInstance_id"`
	// IDText is the text describing the universally unique identifier (UUID) of the market location.
	IDText *string `json:"idText,omitempty"`
	// TypeCode is the code representing the type of market location.
	TypeCode *string `json:"type_code,omitempty"`
	// DirectionCode is the code for the direction of the actor.
	DirectionCode *string `json:"direction_code,omitempty"`
	// Position is the position of the market location.
	Position *int `json:"position,omitempty"`
	// ModelMarketLocationID is the universally unique identifier (UUID) of the model market location.
	ModelMarketLocationID *string `json:"modelMarketLocation_id,omitempty"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID *string `json:"marketLocationId,omitempty"`
	// VirtualMarketLocation indicates whether the market location is virtual.
	VirtualMarketLocation *bool `json:"virtualMarketLocation,omitempty"`
	// AddressID is the universally unique identifier (UUID) of the address to which the market location is assigned.
	AddressID *string `json:"address_id,omitempty"`
	// BillingProcedure is the metering procedure that is used for calculating the billing procedure.
	BillingProcedure *string `json:"billingProcedure,omitempty"`
	// SettlementProcedure is the metering procedure that is used for calculating the settlement procedure.
	SettlementProcedure *string `json:"settlementProcedure,omitempty"`
	// RemovalDate is the date on which the market location is removed.
	RemovalDate *string `json:"removalDate,omitempty"`
	// LocationRemoved indicates whether the market location is removed.
	LocationRemoved *bool `json:"locationRemoved,omitempty"`
	// CommercialSetupDate is the date on which the setup activities for billing, settlement, and other commercial data processing are completed.
	CommercialSetupDate *string `json:"commercialSetupDate,omitempty"`
	// LocationComplete indicates whether the setup for billing, settlement, and other commercial data processing is completed for the whole scope of the measurement concept instance.
	LocationComplete *bool `json:"locationComplete,omitempty"`
	// CalculationRules is the list of calculation rules for this market location.
	CalculationRules []CalculationRule `json:"calculationRules,omitempty"`
}

// MeteringTask represents a metering task assigned to a metering location
// within a measurement concept instance.
type MeteringTask struct {
	// ID is the universally unique identifier (UUID) of the metering task.
	ID string `json:"id"`
	// MeteringLocationID is the universally unique identifier (UUID) of the metering location.
	MeteringLocationID string `json:"meteringLocation_id"`
	// DirectionCode is the code for the direction of the actor.
	DirectionCode *string `json:"direction_code,omitempty"`
	// LossFactorTransformer is the loss factor of the transformer.
	LossFactorTransformer Decimal `json:"lossFactorTransformer,omitempty"`
	// LossFactorLine is the loss factor of the line.
	LossFactorLine Decimal `json:"lossFactorLine,omitempty"`
	// TypeCode is the code representing the type of metering task.
	TypeCode *string `json:"type_code,omitempty"`
	// Position is the position of the metering task.
	Position *int `json:"position,omitempty"`
	// ModelMeteringTasksID is the universally unique identifier (UUID) of the model metering task.
	ModelMeteringTasksID *string `json:"modelMeteringTasks_id,omitempty"`
	// PlannedMeteringProcedureCode is the planned metering procedure code.
	PlannedMeteringProcedureCode *string `json:"plannedMeteringProcedure_code,omitempty"`
	// PlannedRegisterCode is the OBIS-based register code that is planned before the installation of devices.
	PlannedRegisterCode *string `json:"plannedRegisterCode,omitempty"`
	// RegisterCode is the OBIS-based register code that is determined after the installation of devices.
	RegisterCode *string `json:"registerCode,omitempty"`
}

// MeteringLocation represents a metering location within a measurement concept instance.
type MeteringLocation struct {
	// ID is the universally unique identifier (UUID) of the metering location.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID string `json:"measurementConceptInstance_id"`
	// IDText is the text describing the universally unique identifier (UUID) of the metering location.
	IDText string `json:"idText"`
	// TypeCode is the code representing the type of metering location.
	TypeCode *string `json:"type_code,omitempty"`
	// Position is the position of the metering location.
	Position *int `json:"position,omitempty"`
	// ModelMeteringLocationID is the universally unique identifier (UUID) of the model metering location.
	ModelMeteringLocationID *string `json:"modelMeteringLocation_id,omitempty"`
	// MeteringLocationID is the universally unique identifier (UUID) of the metering location.
	MeteringLocationID *string `json:"meteringLocationId,omitempty"`
	// GridCode is the code representing the grid of the metering location.
	GridCode *string `json:"grid_code,omitempty"`
	// GridLevelCode is the code representing the grid level of the metering location.
	GridLevelCode *string `json:"gridLevel_code,omitempty"`
	// AddressID is the universally unique identifier (UUID) of the address to which the metering location is assigned.
	AddressID *string `json:"address_id,omitempty"`
	// LossTransformerSupply is the transformer loss in the Supply direction.
	LossTransformerSupply Decimal `json:"lossTransformerSupply,omitempty"`
	// LossLineSupply is the line loss in the Supply direction.
	LossLineSupply Decimal `json:"lossLineSupply,omitempty"`
	// LossTransformerDemand is the transformer loss in the Demand direction.
	LossTransformerDemand Decimal `json:"lossTransformerDemand,omitempty"`
	// LossLineDemand is the line loss in the Demand direction.
	LossLineDemand Decimal `json:"lossLineDemand,omitempty"`
	// MeteringLocationPurposeCode is the code of the metering location purpose.
	MeteringLocationPurposeCode *string `json:"meteringLocationPurpose_code,omitempty"`
	// Disconnectable indicates whether the metering location can be disconnected.
	Disconnectable *bool `json:"disconnectable,omitempty"`
	// TransformerRequired indicates whether a transformer is required.
	TransformerRequired *bool `json:"transformerRequired,omitempty"`
	// DeviceSerialID is the universally unique identifier (UUID) of the device.
	DeviceSerialID *string `json:"deviceSerialId,omitempty"`
	// RemovalDate is the date on which the metering location is removed.
	RemovalDate *string `json:"removalDate,omitempty"`
	// LocationRemoved indicates whether the metering location is removed.
	LocationRemoved *bool `json:"locationRemoved,omitempty"`
	// InstallationDate is the date on which the metering location is installed.
	InstallationDate *string `json:"installationDate,omitempty"`
	// LocationInstalled indicates whether the metering location is installed.
	LocationInstalled *bool `json:"locationInstalled,omitempty"`
	// MeteringTasks is the list of metering tasks for this metering location.
	MeteringTasks []MeteringTask `json:"meteringTasks,omitempty"`
}

// Actor represents an actor within a measurement concept instance.
type Actor struct {
	// ID is the universally unique identifier (UUID) of the actor.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID string `json:"measurementConceptInstance_id"`
	// IDText is the text describing the universally unique identifier (UUID) of the actor.
	IDText string `json:"idText"`
	// TypeCode is the code representing the type of actor.
	TypeCode *string `json:"type_code,omitempty"`
	// DirectionCode is the code for the direction of the actor.
	DirectionCode *string `json:"direction_code,omitempty"`
	// Position is the position of the actor.
	Position *int `json:"position,omitempty"`
	// ModelActorID is the universally unique identifier (UUID) of the model actor.
	ModelActorID *string `json:"modelActor_id,omitempty"`
	// PowerRangeCode is the code representing the power range of an actor.
	PowerRangeCode *string `json:"powerRange_code,omitempty"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID *string `json:"marketLocation_id,omitempty"`
	// EnergySourceCode is the code representing the energy source of an actor.
	EnergySourceCode *string `json:"energySource_code,omitempty"`
	// AddressID is the universally unique identifier (UUID) of the address to which the actor is assigned.
	AddressID *string `json:"address_id,omitempty"`
	// GridLevelCode is the code representing the grid level of the actor.
	GridLevelCode *string `json:"gridLevel_code,omitempty"`
	// IsOwnConsumption indicates whether the purpose of the metering location is for self-consumption.
	IsOwnConsumption *bool `json:"isOwnConsumption,omitempty"`
}

// OperandMapping represents a mapping of calculation rule operands to metering tasks
// within a measurement concept instance.
type OperandMapping struct {
	// ID is the universally unique identifier (UUID) of the operand mapping.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID string `json:"measurementConceptInstance_id"`
	// Operand is the variables of a formula that are mapped to metering tasks.
	Operand *string `json:"operand,omitempty"`
	// MeteringTaskID is the universally unique identifier (UUID) of the metering task.
	MeteringTaskID *string `json:"meteringTask_id,omitempty"`
	// Position is the position of the operand mapping.
	Position *int `json:"position,omitempty"`
}

// InstanceCharacteristic represents a characteristic associated with a change process
// of a measurement concept instance.
type InstanceCharacteristic struct {
	// ID is the universally unique identifier (UUID) of the characteristic.
	ID string `json:"id"`
	// ChangeProcessID is the universally unique identifier (UUID) of the change process.
	ChangeProcessID string `json:"changeProcess_id"`
	// EntityTypeCode is the code of the entity that is associated with the characteristic.
	EntityTypeCode *string `json:"entityType_code,omitempty"`
	// ModelEntityID is the universally unique identifier (UUID) of the model entity.
	ModelEntityID *string `json:"modelEntityId,omitempty"`
	// CharacteristicCode is the code of the characteristic.
	CharacteristicCode *string `json:"characteristic_code,omitempty"`
	// Value is the value of the characteristic.
	Value *string `json:"value,omitempty"`
}

// ChangeProcess represents a change process for a measurement concept instance.
type ChangeProcess struct {
	// ID is the universally unique identifier (UUID) of the change process.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstanceID string `json:"measurementConceptInstance_id"`
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
	// ProcessData is the expanded process data navigation property.
	ProcessData *InstanceProcessData `json:"processData,omitempty"`
	// InstanceCharacteristics is the list of characteristics for this change process.
	InstanceCharacteristics []InstanceCharacteristic `json:"instanceCharacteristics,omitempty"`
}

// MeasurementConceptInstance represents a measurement concept instance returned by the API.
type MeasurementConceptInstance struct {
	// ID is the universally unique identifier (UUID) of the measurement concept instance.
	ID string `json:"id"`
	// IDText is the text describing the universally unique identifier (UUID) of the measurement concept instance.
	IDText string `json:"idText"`
	// Version is the version of the measurement concept instance.
	Version *string `json:"version,omitempty"`
	// Description is the description of the measurement concept instance.
	Description *string `json:"description,omitempty"`
	// LeadingGridCode is the code representing the leading grid of the measurement concept instance.
	LeadingGridCode *string `json:"leadingGrid_code,omitempty"`
	// DivisionCode is the code representing the division of the measurement concept instance.
	DivisionCode *string `json:"division_code,omitempty"`
	// OrdererCode is the code representing the orderer of the measurement concept instance.
	OrdererCode *string `json:"orderer_code,omitempty"`
	// LeadingAddressID is the universally unique identifier (UUID) of the leading address of the measurement concept instance.
	LeadingAddressID *string `json:"leadingAddress_id,omitempty"`
	// PredecessorID is the universally unique identifier (UUID) of the preceding version of the measurement concept instance.
	PredecessorID *string `json:"predecessor_id,omitempty"`
	// Difference2PredecessorMeasurementConceptInstanceID is the universally unique identifier (UUID) of the predecessor version of the measurement concept instance.
	Difference2PredecessorMeasurementConceptInstanceID *string `json:"difference2Predecessor_measurementConceptInstance_id,omitempty"`
	// MeasurementModelID is the universally unique identifier (UUID) of the measurement concept model that is referenced by the measurement concept instance.
	MeasurementModelID *string `json:"measurementModel_id,omitempty"`
	// MeasurementClassID is the universally unique identifier (UUID) of the measurement concept class that is referenced by the measurement concept instance.
	MeasurementClassID *string `json:"measurementClass_id,omitempty"`
	// OverallStatusCode is the combined status of the status and the process status of the measurement concept instance.
	OverallStatusCode *string `json:"overallStatus_code,omitempty"`
	// StatusID is the universally unique identifier (UUID) of the status of the measurement concept instance.
	StatusID *string `json:"status_id,omitempty"`
	// ModifiedAt is the date and time at which the measurement concept instance was last modified.
	ModifiedAt *time.Time `json:"modifiedAt,omitempty"`
	// ModifiedBy is the user who last modified the measurement concept instance.
	ModifiedBy *string `json:"modifiedBy,omitempty"`
	// InstalledOn is the date on which the physical installation processes are completed for a version of the measurement concept instance.
	InstalledOn *string `json:"installedOn,omitempty"`
	// InstalledUntil is the date until a version of a measurement concept instance is valid.
	InstalledUntil *string `json:"installedUntil,omitempty"`
	// CommercialSetupOn is the date on which the commercial setup processes are completed for a version of a measurement concept instance.
	CommercialSetupOn *string `json:"commercialSetupOn,omitempty"`
	// PhysicalShutdownOn is the date on which the physical shutdown processes are completed for a version of a measurement concept instance.
	PhysicalShutdownOn *string `json:"physicalShutdownOn,omitempty"`
	// CommercialShutdownOn is the date on which the commercial shutdown processes are completed for a version of a measurement concept instance.
	CommercialShutdownOn *string `json:"commercialShutdownOn,omitempty"`
	// DeviceInstallationsReady indicates whether the metering devices are installed for the measurement concept instance.
	DeviceInstallationsReady *bool `json:"deviceInstallationsReady,omitempty"`
	// MarketLocationsComplete indicates whether all the setup of data processing for billing and similar purposes is finished.
	MarketLocationsComplete *bool `json:"marketLocationsComplete,omitempty"`
	// MeteringLocations is the list of metering locations in this instance.
	MeteringLocations []MeteringLocation `json:"meteringLocations,omitempty"`
	// MarketLocations is the list of market locations in this instance.
	MarketLocations []MarketLocation `json:"marketLocations,omitempty"`
	// OperandMappings is the list of operand mappings in this instance.
	OperandMappings []OperandMapping `json:"operandMappings,omitempty"`
	// Actors is the list of actors in this instance.
	Actors []Actor `json:"actors,omitempty"`
	// Addresses is the list of addresses associated with this instance.
	Addresses []InstanceAddress `json:"addresses,omitempty"`
	// ChangeProcesses is the list of change processes in this instance.
	ChangeProcesses []ChangeProcess `json:"changeProcesses,omitempty"`
	// Statuses is the list of status entries for this instance.
	Statuses []InstanceStatus `json:"status,omitempty"`
}

// InstanceAddress represents a geographic and postal address associated with
// a measurement concept instance.
type InstanceAddress struct {
	// ID is the universally unique identifier (UUID) of the object address.
	ID string `json:"id"`
	// MeasurementConceptInstanceID is the UUID of the measurement concept instance.
	MeasurementConceptInstanceID string `json:"measurementConceptInstance_id"`
	// CountryCode is the code representing the country/region.
	CountryCode *string `json:"country_code,omitempty"`
	// CityID is the city ID.
	CityID *string `json:"cityID,omitempty"`
	// CityName is the name of the city.
	CityName *string `json:"cityName,omitempty"`
	// PostalCode is the postal code.
	PostalCode *string `json:"postalCode,omitempty"`
	// CityDistrict is the city district in which the address object resides.
	CityDistrict *string `json:"cityDistrict,omitempty"`
	// StreetID is the street ID.
	StreetID *string `json:"streetID,omitempty"`
	// StreetName is the name of the street.
	StreetName *string `json:"streetName,omitempty"`
	// HouseNumber is the number of the premise.
	HouseNumber *string `json:"houseNumber,omitempty"`
	// HouseNumberSupplement is the supplement of the house number.
	HouseNumberSupplement *string `json:"houseNumberSupplement,omitempty"`
	// FloorNumber is the floor number of the premise.
	FloorNumber *string `json:"floorNumber,omitempty"`
	// Supplement is the supplement of the address object.
	Supplement *string `json:"supplement,omitempty"`
	// Latitude is the latitude of the address.
	Latitude *Decimal `json:"latitude,omitempty"`
	// Longitude is the longitude of the address.
	Longitude *Decimal `json:"longitude,omitempty"`
	// TimeZone is the time zone of the address.
	TimeZone *string `json:"timeZone,omitempty"`
}

// InstanceStatus holds the instance status and process status codes
// for a measurement concept instance.
type InstanceStatus struct {
	// ID is the universally unique identifier (UUID) of the status.
	ID string `json:"id"`
	// ChangeProcessID is the UUID of the associated change process.
	ChangeProcessID string `json:"changeProcess_id"`
	// MeasurementConceptInstanceID is the UUID of the measurement concept instance.
	MeasurementConceptInstanceID *string `json:"measurementConceptInstance_id,omitempty"`
	// InstanceStatusCode is the status code of the measurement concept instance.
	InstanceStatusCode *string `json:"instanceStatus_code,omitempty"`
	// ProcessStatusCode is the process status code of the measurement concept instance.
	ProcessStatusCode *string `json:"processStatus_code,omitempty"`
}

// --- Input / Create structs ---

// CreateInstanceInput is the request body for creating a measurement concept instance.
type CreateInstanceInput struct {
	// Description is the brief description of the measurement concept instance.
	Description *string `json:"description,omitempty"`
	// MeasurementModelID is the universally unique identifier of the measurement concept model from which the measurement concept is instantiated.
	MeasurementModelID string `json:"measurementModel_id"`
	// LeadingGridCode is the code representing the leading grid of the measurement concept instance.
	LeadingGridCode *string `json:"leadingGrid_code,omitempty"`
	// DivisionCode is the code representing the division of the measurement concept instance.
	DivisionCode *string `json:"division_code,omitempty"`
	// OrdererCode is the code representing the orderer of the measurement concept instance.
	OrdererCode *string `json:"orderer_code,omitempty"`
	// Addresses is the list of addresses for the new instance.
	Addresses []CreateAddressInput `json:"addresses,omitempty"`
	// ChangeProcesses is the list of change processes for the new instance.
	ChangeProcesses []CreateChangeProcessInput `json:"changeProcesses,omitempty"`
}

// CreateAddressInput is the address portion of a create instance request.
type CreateAddressInput struct {
	// CountryCode is the code representing the country/region.
	CountryCode *string `json:"country_code,omitempty"`
	// CityID is the city ID.
	CityID *string `json:"cityID,omitempty"`
	// CityName is the name of the city.
	CityName *string `json:"cityName,omitempty"`
	// PostalCode is the postal code.
	PostalCode *string `json:"postalCode,omitempty"`
	// StreetID is the street ID.
	StreetID *string `json:"streetID,omitempty"`
	// StreetName is the name of the street.
	StreetName *string `json:"streetName,omitempty"`
	// HouseNumber is the number of the premise.
	HouseNumber *string `json:"houseNumber,omitempty"`
	// Latitude is the latitude of the address.
	Latitude *Decimal `json:"latitude,omitempty"`
	// Longitude is the longitude of the address.
	Longitude *Decimal `json:"longitude,omitempty"`
	// TimeZone is the time zone of the address.
	TimeZone *string `json:"timeZone,omitempty"`
}

// CreateChangeProcessInput is the change process portion of a create instance request.
// Note: for create operations, instanceCharacteristics is at the changeProcess level,
// not nested inside processData (unlike initChange where it's inside processData).
type CreateChangeProcessInput struct {
	// ExternalOrderID is the ID of the external order.
	ExternalOrderID string `json:"externalOrderId"`
	// ProcessData is the process data for the creation.
	ProcessData *CreateProcessDataInput `json:"processData,omitempty"`
	// InstanceCharacteristics is the list of characteristics for the creation.
	InstanceCharacteristics []InstanceCharacteristicInput `json:"instanceCharacteristics,omitempty"`
}

// CreateProcessDataInput is the process data for a create instance request.
type CreateProcessDataInput struct {
	// CustomerRequestDate is the date on which a customer requests the change process.
	CustomerRequestDate *string `json:"customerRequestDate,omitempty"`
	// LeadingConnectionUser is the ILN of the utility connection user.
	LeadingConnectionUser *string `json:"leadingConnectionUser,omitempty"`
	// LeadingConnectionOwner is the ILN of the utility connection owner.
	LeadingConnectionOwner *string `json:"leadingConnectionOwner,omitempty"`
	// Note is a free-text note related to the process.
	Note *string `json:"note,omitempty"`
}

// UpdateInstanceInput is the request body for updating a measurement concept instance.
type UpdateInstanceInput struct {
	// LeadingAddressID is the universally unique identifier (UUID) of the leading address of the measurement concept instance.
	LeadingAddressID *string `json:"leadingAddress_id,omitempty"`
}

// UpdateMeteringLocationInput is the request body for updating a metering location
// of a measurement concept instance.
type UpdateMeteringLocationInput struct {
	// GridLevelCode is the code representing the grid level of the metering location.
	GridLevelCode *string `json:"gridLevel_code,omitempty"`
	// Disconnectable indicates whether the metering location can be disconnected.
	Disconnectable *bool `json:"disconnectable,omitempty"`
	// TransformerRequired indicates whether a transformer is required.
	TransformerRequired *bool `json:"transformerRequired,omitempty"`
	// InstallationDate is the date on which the metering location is installed.
	InstallationDate *string `json:"installationDate,omitempty"`
	// DeviceSerialID is the universally unique identifier (UUID) of the device.
	DeviceSerialID *string `json:"deviceSerialId,omitempty"`
	// MeteringLocationID is the universally unique identifier (UUID) of the metering location.
	MeteringLocationID *string `json:"meteringLocationId,omitempty"`
}

// UpdateMarketLocationInput is the request body for updating a market location
// of a measurement concept instance.
type UpdateMarketLocationInput struct {
	// MarketLocationID is the ID of the market location.
	MarketLocationID *string `json:"marketLocationId,omitempty"`
}

// UpdateActorInput is the request body for updating an actor
// of a measurement concept instance.
type UpdateActorInput struct {
	// EnergySourceCode is the code representing the energy source of an actor.
	EnergySourceCode *string `json:"energySource_code,omitempty"`
	// SubTypeCode is the subtype of an actor.
	SubTypeCode *string `json:"subType_code,omitempty"`
	// InstallationDate is the date on which an actor is installed.
	InstallationDate *string `json:"installationDate,omitempty"`
	// CommercialSetupDate is the date on which the setup activities for billing, settlement, and other commercial data processing are completed.
	CommercialSetupDate *string `json:"commercialSetupDate,omitempty"`
}

// UpdateMeteringTaskInput is the request body for updating a metering task
// of a measurement concept instance.
type UpdateMeteringTaskInput struct {
	// RegisterCode is the OBIS-based register code that is determined after the installation of devices.
	RegisterCode *string `json:"registerCode,omitempty"`
}

// UpdateOperandMappingInput is the request body for updating the operand mapping
// of a measurement concept instance.
type UpdateOperandMappingInput struct {
	// Value is the value of the variable.
	Value string `json:"value"`
}

// InitChangeInput is the request body for initiating a change process
// on a measurement concept instance.
type InitChangeInput struct {
	// DataForNewInstanceVersion contains the data for the new instance version.
	DataForNewInstanceVersion []InitChangeVersionData `json:"dataForNewInstanceVersion"`
}

// InitChangeVersionData contains the data for the new instance version
// in an initChange request.
type InitChangeVersionData struct {
	// Description is the brief description of the changed version of measurement concept instance.
	Description *string `json:"description,omitempty"`
	// MeasurementModelID is the universally unique identifier of the measurement concept model from which the measurement concept is instantiated.
	MeasurementModelID string `json:"measurementModel_id"`
	// ChangeProcesses is the list of change processes for this version.
	ChangeProcesses []InitChangeProcessInput `json:"changeProcesses,omitempty"`
}

// InitChangeProcessInput is the change process portion of an initChange request.
type InitChangeProcessInput struct {
	// ExternalOrderID is the ID of the external order that corresponds to the instantiation of the measurement concept.
	ExternalOrderID *string `json:"externalOrderId,omitempty"`
	// ProcessData is the process data for the change.
	ProcessData *InitChangeProcessDataInput `json:"processData,omitempty"`
}

// InitChangeProcessDataInput is the process data for an initChange request.
type InitChangeProcessDataInput struct {
	// CustomerRequestDate is the date on which a customer requests the change process for a measurement concept instance.
	CustomerRequestDate *string `json:"customerRequestDate,omitempty"`
	// InstanceCharacteristics is the list of characteristics for the change.
	InstanceCharacteristics []InstanceCharacteristicInput `json:"instanceCharacteristics,omitempty"`
}

// InstanceCharacteristicInput is the input for creating or changing a characteristic
// of a measurement concept instance.
type InstanceCharacteristicInput struct {
	// EntityTypeCode is the code representing the resource from which the characteristic of the measurement concept instance originates.
	EntityTypeCode *string `json:"entityType_code,omitempty"`
	// CharacteristicCode is the code representing the characteristic of the measurement concept instance.
	CharacteristicCode *string `json:"characteristic_code,omitempty"`
	// ModelEntityID is the universally unique identifier (UUID) of the model entity.
	ModelEntityID *string `json:"modelEntityId,omitempty"`
	// Value is the value that is assigned to the characteristic of the measurement concept instance.
	Value *string `json:"value,omitempty"`
}

// InitMergeInput is the request body for initiating a merge of
// measurement concept instances.
type InitMergeInput struct {
	// DataForNewInstanceVersion contains the data for the new merged instance version.
	DataForNewInstanceVersion *InitMergeVersionData `json:"dataForNewInstanceVersion"`
}

// InitMergeVersionData contains the data for the new merged instance version.
type InitMergeVersionData struct {
	// Description is the brief description of the merge of measurement concept instances.
	Description *string `json:"description,omitempty"`
	// MeasurementModelID is the universally unique identifier of the measurement concept model from which the measurement concept is instantiated.
	MeasurementModelID string `json:"measurementModel_id"`
	// ToBeMergedAncestors is the list of ancestor instances to be merged.
	ToBeMergedAncestors []AncestorRef `json:"toBeMergedAncestors"`
	// ChangeProcesses is the list of change processes for the merge.
	ChangeProcesses []InitMergeChangeProcessInput `json:"changeProcesses"`
}

// AncestorRef references an instance version which shall be merged.
type AncestorRef struct {
	// ID is the universally unique identifier (UUID) of the measurement concept instance.
	ID string `json:"id"`
	// IDText is the universally unique identifier (UUID) of the text.
	IDText string `json:"idText"`
}

// InitMergeChangeProcessInput is the change process portion of a merge request.
type InitMergeChangeProcessInput struct {
	// ExternalOrderID is the ID of the external order that corresponds to the instantiation of the measurement concept.
	ExternalOrderID *string `json:"externalOrderId,omitempty"`
	// ProcessData *InitMergeProcessDataInput is the process data for the merge.
	ProcessData *InitMergeProcessDataInput `json:"processData,omitempty"`
}

// InitMergeProcessDataInput is the process data for a merge request.
type InitMergeProcessDataInput struct {
	// CustomerRequestDate is the date on which a customer requests the merge process for a measurement concept instance.
	CustomerRequestDate *string `json:"customerRequestDate,omitempty"`
	// LeadingConnectionOwner is the ID of the owner of the utility connection that is provided with the measurement concept instance.
	LeadingConnectionOwner *string `json:"leadingConnectionOwner,omitempty"`
	// LeadingConnectionUser is the ID of the user of the utility connection that is provided with the measurement concept instance.
	LeadingConnectionUser *string `json:"leadingConnectionUser,omitempty"`
	// Note is the note related to the process.
	Note *string `json:"note,omitempty"`
	// InstanceCharacteristics is the list of characteristics for the merge.
	InstanceCharacteristics []MergeInstanceCharacteristicInput `json:"instanceCharacteristics,omitempty"`
}

// MergeInstanceCharacteristicInput is the input for merge characteristics.
type MergeInstanceCharacteristicInput struct {
	// CharacteristicCode is the code representing the characteristic of the measurement concept instance.
	CharacteristicCode *string `json:"characteristic_code,omitempty"`
	// ModelEntityID is the universally unique identifier (UUID) of the model entity.
	ModelEntityID *string `json:"modelEntityId,omitempty"`
	// EntityTypeCode is the code representing the resource from which the characteristic of the measurement concept instance originates.
	EntityTypeCode *string `json:"entityType_code,omitempty"`
	// Value is the value that is assigned to the characteristic of the measurement concept instance.
	Value *string `json:"value,omitempty"`
	// PredecessorRepetitionIndex is the code representing the resource from which the characteristic of the measurement concept instance originates.
	PredecessorRepetitionIndex *string `json:"predecessorRepetitionIndex,omitempty"`
	// SourceEntityID is the universally unique identifier (UUID) of the source entity.
	SourceEntityID *string `json:"sourceEntityId,omitempty"`
	// SourceIDText is the source ID text.
	SourceIDText *string `json:"sourceIdText,omitempty"`
	// TargetIDText is the target ID text.
	TargetIDText *string `json:"targetIdText,omitempty"`
}

// InitShutdownInput is the request body for initiating a shutdown of
// a measurement concept instance.
type InitShutdownInput struct {
	// DataForNewInstanceVersion contains the data for the shutdown.
	DataForNewInstanceVersion []InitShutdownVersionData `json:"dataForNewInstanceVersion"`
}

// InitShutdownVersionData contains the shutdown change processes.
type InitShutdownVersionData struct {
	// ChangeProcesses is the list of change processes for the shutdown.
	ChangeProcesses []InitShutdownChangeProcessInput `json:"changeProcesses"`
}

// InitShutdownChangeProcessInput is the change process portion of a shutdown request.
type InitShutdownChangeProcessInput struct {
	// ExternalOrderID is the ID of the external order that corresponds to the instantiation of the measurement concept.
	ExternalOrderID *string `json:"externalOrderId,omitempty"`
	// ProcessReasonCode is the reason code for initiating a shutdown.
	ProcessReasonCode *string `json:"processReason_Code,omitempty"`
	// ProcessData is the process data for the shutdown.
	ProcessData *InitShutdownProcessDataInput `json:"processData,omitempty"`
}

// InitShutdownProcessDataInput is the process data for a shutdown request.
type InitShutdownProcessDataInput struct {
	// CustomerRequestDate is the date on which a customer requests for shutdown for a measurement concept instance.
	CustomerRequestDate *string `json:"customerRequestDate,omitempty"`
}

// InitVersionCancelInput is the request body for initiating a version cancel of
// a measurement concept instance.
type InitVersionCancelInput struct {
	// DataForNewInstanceVersion contains the data for the version cancel.
	DataForNewInstanceVersion *InitVersionCancelVersionData `json:"dataForNewInstanceVersion"`
}

// InitVersionCancelVersionData contains the version cancel change processes.
type InitVersionCancelVersionData struct {
	// ChangeProcesses is the list of change processes for the version cancel.
	ChangeProcesses []InitVersionCancelChangeProcessInput `json:"changeProcesses,omitempty"`
}

// InitVersionCancelChangeProcessInput is the change process portion of a version cancel request.
type InitVersionCancelChangeProcessInput struct {
	// CancellationReason is the reason for the cancellation.
	CancellationReason *string `json:"cancellationReason,omitempty"`
}
