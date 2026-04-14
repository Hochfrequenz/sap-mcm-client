package mcm

import "time"

// ActorPDExternalReference represents an external reference associated with
// actor process data in a measurement concept instance.
type ActorPDExternalReference struct {
	// ID is the universally unique identifier (UUID) of the external reference.
	ID string `json:"id"`
	// ModifiedAt is the date and time at which the external reference was last modified.
	ModifiedAt *time.Time `json:"modifiedAt,omitempty"`
	// CreatedAt is the date and time at which the external reference was created.
	CreatedAt *time.Time `json:"createdAt,omitempty"`
	// CreatedBy is the user who created the external reference.
	CreatedBy *string `json:"createdBy,omitempty"`
	// ModifiedBy is the user who last modified the external reference.
	ModifiedBy *string `json:"modifiedBy,omitempty"`
	// CreatedByUUID is the universally unique identifier (UUID) of the user who created the external reference.
	CreatedByUUID *string `json:"createdByUuid,omitempty"`
	// ModifiedByUUID is the universally unique identifier (UUID) of the user who last modified the external reference.
	ModifiedByUUID *string `json:"modifiedByUuid,omitempty"`
	// ActorPDID is the universally unique identifier (UUID) of the actor.
	ActorPDID string `json:"actorPD_id"`
	// ReferenceTypeCode is the code for the type of external reference.
	ReferenceTypeCode *string `json:"referenceType_code,omitempty"`
	// ReferenceSystemCode is the code for the system wherein the reference is stored.
	ReferenceSystemCode *string `json:"referenceSystem_code,omitempty"`
	// ReferenceID is the ID of the external reference.
	ReferenceID *string `json:"referenceId,omitempty"`
	// Position is the position of the external reference.
	Position *int `json:"position,omitempty"`
}

// ActorPD represents the process data of an actor for a measurement concept instance.
type ActorPD struct {
	// ID is the universally unique identifier (UUID) of the actor.
	ID string `json:"id"`
	// MeasurementConceptInstancePDID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstancePDID string `json:"measurementConceptInstancePD_id"`
	// ActorID is the universally unique identifier (UUID) of the actor.
	ActorID string `json:"actor_id"`
	// Position is the position of the actor.
	Position *int `json:"position,omitempty"`
	// PlannedInstalledPower is the planned installed power of the actor.
	PlannedInstalledPower Decimal `json:"plannedInstalledPower,omitempty"`
	// InstalledPower is the installed power of the actor.
	InstalledPower Decimal `json:"installedPower,omitempty"`
	// InverterPower is the inverter power of the actor.
	InverterPower Decimal `json:"inverterPower,omitempty"`
	// ExternalReferences is the list of external references for this actor.
	ExternalReferences []ActorPDExternalReference `json:"externalReferences,omitempty"`
}

// MeteringTaskPD represents the process data of a metering task
// for a measurement concept instance.
type MeteringTaskPD struct {
	// ID is the universally unique identifier (UUID) of the metering task.
	ID string `json:"id"`
	// MeteringLocationPDID is the universally unique identifier (UUID) of the metering location to which the metering task is assigned.
	MeteringLocationPDID string `json:"meteringLocationPD_id"`
	// MeteringTaskID is the universally unique identifier (UUID) of the metering task.
	MeteringTaskID *string `json:"meteringTask_id,omitempty"`
	// Position is the position of the metering task.
	Position *int `json:"position,omitempty"`
	// RateCode is the tariff code of the metering task.
	RateCode *string `json:"rate_code,omitempty"`
	// PeriodConsumption is the consumption over a one-year period provided as a positive value in kWh.
	PeriodConsumption Decimal `json:"periodConsumption,omitempty"`
}

// MeteringLocationPD represents the process data of a metering location
// for a measurement concept instance.
type MeteringLocationPD struct {
	// ID is the universally unique identifier (UUID) of the metering location.
	ID string `json:"id"`
	// MeasurementConceptInstancePDID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstancePDID string `json:"measurementConceptInstancePD_id"`
	// MeteringLocationID is the universally unique identifier (UUID) of the metering location.
	MeteringLocationID *string `json:"meteringLocation_id,omitempty"`
	// Position is the position of the metering location.
	Position *int `json:"position,omitempty"`
	// PlannedMeteringLocationID is the ID of a customer's own metering location.
	PlannedMeteringLocationID *string `json:"plannedMeteringLocationId,omitempty"`
	// DeviceLocationSupplement is the supplementary information about the location of a device, acting as a hint for electricians.
	DeviceLocationSupplement *string `json:"deviceLocationSupplement,omitempty"`
	// MeterOperator is the unique identifier (ILN) of the meter operator.
	MeterOperator *string `json:"meterOperator,omitempty"`
	// Note is the user-provided information about the metering location.
	Note *string `json:"note,omitempty"`
	// Classification is the classification of the metering location such as household, streetlight, shop, and restaurant.
	Classification *string `json:"classification,omitempty"`
	// MeasuringTypeCode is the code for the type of measuring device.
	MeasuringTypeCode *string `json:"measuringType_code,omitempty"`
	// VolumeCorrector indicates whether the volume corrector is set.
	VolumeCorrector *bool `json:"volumeCorrector,omitempty"`
	// NominalCapacity is the nominal capacity of the metering location.
	NominalCapacity Decimal `json:"nominalCapacity,omitempty"`
	// LocationIdentifierReady indicates whether the completion of settings point of delivery IDs can be signaled.
	LocationIdentifierReady *bool `json:"locationIdentifierReady,omitempty"`
	// MasterDataReady indicates whether all parameters related to master data readiness are set to true.
	MasterDataReady *bool `json:"masterDataReady,omitempty"`
	// CalorificValueDistrict is the calorific value district of the metering location that is used in the gas division.
	CalorificValueDistrict *string `json:"calorificValueDistrict,omitempty"`
	// InstallationDate is the date on which the metering location is installed.
	InstallationDate *string `json:"installationDate,omitempty"`
	// LocationInstalled indicates whether the metering location is installed.
	LocationInstalled *bool `json:"locationInstalled,omitempty"`
	// RemovalDate is the date on which the metering location is removed.
	RemovalDate *string `json:"removalDate,omitempty"`
	// LocationRemoved indicates whether the metering location is removed.
	LocationRemoved *bool `json:"locationRemoved,omitempty"`
	// LocationCode is the location code for metering location.
	// Note: this field appears only in the update spec (MCIMeteringLocationsPD-update),
	// not in the response spec. Included here for forward compatibility — the API
	// may return it even though the spec doesn't document it in responses.
	LocationCode *string `json:"locationCode,omitempty"`
	// MeteringTasksPD is the list of metering task process data.
	MeteringTasksPD []MeteringTaskPD `json:"meteringTasksPD,omitempty"`
}

// MarketLocationPD represents the process data of a market location
// for a measurement concept instance.
type MarketLocationPD struct {
	// ID is the universally unique identifier (UUID) of the market location.
	ID string `json:"id"`
	// MeasurementConceptInstancePDID is the universally unique identifier (UUID) of the measurement concept instance.
	MeasurementConceptInstancePDID string `json:"measurementConceptInstancePD_id"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID *string `json:"marketLocation_id,omitempty"`
	// Position is the position of the market location.
	Position *int `json:"position,omitempty"`
	// ConnectionUser is the ID of the user of the utility connection that is provided with the measurement concept instance.
	ConnectionUser *string `json:"connectionUser,omitempty"`
	// ConnectionOwner is the ID of the owner of the utility connection that is provided with the measurement concept instance.
	ConnectionOwner *string `json:"connectionOwner,omitempty"`
	// ForecastBasisCode is the code of the forecast basis of the market location.
	ForecastBasisCode *string `json:"forecastBasis_code,omitempty"`
	// ConsumptionDistribution is the consumption distribution of the market location.
	ConsumptionDistribution *string `json:"consumptionDistribution,omitempty"`
	// FlatrateTypeCode is the code of the type of flat rate.
	FlatrateTypeCode *string `json:"flatrateType_code,omitempty"`
	// Flatrate is the flat rate of the market location.
	Flatrate *string `json:"flatrate,omitempty"`
	// Classification is the classification of a market location such as household, streetlight, shop, and restaurant.
	Classification *string `json:"classification,omitempty"`
	// DirectSelling indicates whether the market location supports direct selling.
	DirectSelling *bool `json:"directSelling,omitempty"`
	// ConnectionOperator is the operator of the connection of the market location.
	ConnectionOperator *string `json:"connectionOperator,omitempty"`
	// LocationIdentifierReady indicates whether the completion of settings point of delivery IDs can be signaled.
	LocationIdentifierReady *bool `json:"locationIdentifierReady,omitempty"`
	// MasterDataReady indicates whether all parameters related to master data readiness are set to true.
	MasterDataReady *bool `json:"masterDataReady,omitempty"`
	// CommercialSetupDate is the date on which the setup activities for billing, settlement, and other commercial data processing are completed.
	CommercialSetupDate *string `json:"commercialSetupDate,omitempty"`
	// LocationComplete indicates whether the setup for billing, settlement, and other commercial data processing is completed for the entire scope of the measurement concept instance.
	LocationComplete *bool `json:"locationComplete,omitempty"`
	// LocationRemoved indicates whether the market location is removed.
	LocationRemoved *bool `json:"locationRemoved,omitempty"`
	// RemovalDate is the date on which the market location is removed.
	RemovalDate *string `json:"removalDate,omitempty"`
	// CommunalInstallation is the communal installation of the market location.
	CommunalInstallation *bool `json:"communalInstallation,omitempty"`
}

// InstanceProcessData represents the process data for a measurement concept instance,
// associated with a change process.
type InstanceProcessData struct {
	// ID is the universally unique identifier (UUID) of the process data of the measurement concept instance.
	ID string `json:"id"`
	// ChangeProcessID is the universally unique identifier (UUID) of the change process.
	ChangeProcessID string `json:"changeProcess_id"`
	// SubscriberID is the ID of the subscriber.
	SubscriberID *string `json:"subscriberId,omitempty"`
	// LeadingConnectionUser is the ID of the user of the utility connection that is provided with the measurement concept instance.
	LeadingConnectionUser *string `json:"leadingConnectionUser,omitempty"`
	// LeadingConnectionOwner is the ID of the owner of the utility connection that is provided with the measurement concept instance.
	LeadingConnectionOwner *string `json:"leadingConnectionOwner,omitempty"`
	// Note is the user-provided information about the measurement concept instance.
	Note *string `json:"note,omitempty"`
	// InitialDataEntryReady indicates whether a pre-system is enabled to notify the measurement concept management component about the readiness of DSO's first data entry for a measurement concept instance.
	InitialDataEntryReady *bool `json:"initialDataEntryReady,omitempty"`
	// LocationIdentifiersReady indicates whether the completion of settings point of delivery IDs can be signaled.
	LocationIdentifiersReady *bool `json:"locationIdentifiersReady,omitempty"`
	// FinalDataEntryReady indicates whether the point of delivery IDs are known for each location and that interested parties can read those IDs to continue and distribute the point of delivery IDs in their process and data.
	FinalDataEntryReady *bool `json:"finalDataEntryReady,omitempty"`
	// MasterDataReady indicates whether all parameters related to master data readiness are set to true.
	MasterDataReady *bool `json:"masterDataReady,omitempty"`
	// DeviceInstallationsReady indicates whether all devices were installed at physical locations corresponding to the metering locations and that relevant data is set.
	DeviceInstallationsReady *bool `json:"deviceInstallationsReady,omitempty"`
	// MarketLocationsComplete indicates whether all the setup for billing, settlement, and other commercial data processing is completed for the entire scope of the measurement concept instance.
	MarketLocationsComplete *bool `json:"marketLocationsComplete,omitempty"`
	// MeteringLocationsPD is the list of metering location process data.
	MeteringLocationsPD []MeteringLocationPD `json:"meteringLocationsPD,omitempty"`
	// MarketLocationsPD is the list of market location process data.
	MarketLocationsPD []MarketLocationPD `json:"marketLocationsPD,omitempty"`
	// ActorsPD is the list of actor process data.
	ActorsPD []ActorPD `json:"actorsPD,omitempty"`
}

// --- Process data update inputs ---

// UpdateMeteringLocationPDInput is the request body for updating the process data
// of a metering location within a measurement concept instance.
type UpdateMeteringLocationPDInput struct {
	// Classification is the classification of the metering location such as household, streetlight, shop, and restaurant.
	Classification *string `json:"classification,omitempty"`
	// Note is the user-provided information about the metering location.
	Note *string `json:"note,omitempty"`
	// VolumeCorrector indicates whether the volume corrector is set.
	VolumeCorrector *bool `json:"volumeCorrector,omitempty"`
	// MeterOperator is the unique identifier (ILN) of the meter operator.
	MeterOperator *string `json:"meterOperator,omitempty"`
	// NominalCapacity is the nominal capacity of the metering location.
	NominalCapacity Decimal `json:"nominalCapacity,omitempty"`
	// MeasuringTypeCode is the code for the type of measuring device.
	MeasuringTypeCode *string `json:"measuringType_code,omitempty"`
	// LocationCode is the location code for metering location.
	LocationCode *string `json:"locationCode,omitempty"`
}

// UpdateMeteringTaskPDInput is the request body for updating the process data
// of a metering task within a measurement concept instance.
type UpdateMeteringTaskPDInput struct {
	// RateCode is the tariff code of the metering task.
	RateCode *string `json:"rate_code,omitempty"`
	// PeriodConsumption is the consumption over a one-year period provided as a positive value in kWh.
	PeriodConsumption Decimal `json:"periodConsumption,omitempty"`
}

// UpdateMarketLocationPDInput is the request body for updating the process data
// of a market location within a measurement concept instance.
type UpdateMarketLocationPDInput struct {
	// Classification is the classification of the market location such as household, streetlight, shop, and restaurant.
	Classification *string `json:"classification,omitempty"`
	// ConnectionUser is the ID of the user of the utility connection that is provided with the measurement concept instance.
	ConnectionUser *string `json:"connectionUser,omitempty"`
	// ConnectionOwner is the ID of the owner of the utility connection that is provided with the measurement concept instance.
	ConnectionOwner *string `json:"connectionOwner,omitempty"`
	// ForecastBasisCode is the code of the forecast basis of the market location.
	ForecastBasisCode *string `json:"forecastBasis_code,omitempty"`
	// ConsumptionDistribution is the consumption distribution of the market location.
	ConsumptionDistribution *string `json:"consumptionDistribution,omitempty"`
	// CommercialSetupDate is the date on which the setup activities for billing, settlement, and other commercial data processing are completed.
	CommercialSetupDate *string `json:"commercialSetupDate,omitempty"`
}
