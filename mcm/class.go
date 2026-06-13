package mcm

// CodeNameDescription is a reusable struct for code-list expansions
// that contain a code, name, and description (e.g., division types,
// direction types).
type CodeNameDescription struct {
	// Code is the identifier code for the entry.
	Code string `json:"code"`
	// Name is the brief description of the entry.
	Name *string `json:"name,omitempty"`
	// Descr is the long description of the entry.
	Descr *string `json:"descr,omitempty"`
}

// MCClassType is the expanded classType navigation property of a
// measurement concept class (OData type MCClassTypes). In addition to the
// usual code/name/description triple it carries three capability flags that
// indicate whether classes of this type may be modified.
type MCClassType struct {
	// Code is the code representing the class type (e.g., "CLASS" or "SAPTEMPLATE").
	Code string `json:"code"`
	// Name is the brief description of the type of a measurement concept class.
	Name *string `json:"name,omitempty"`
	// Descr is the long description of the type of a measurement concept class.
	Descr *string `json:"descr,omitempty"`
	// ReadOnly indicates whether measurement concept classes of this type are read-only.
	ReadOnly *bool `json:"readOnly,omitempty"`
	// Deletable indicates whether measurement concept classes of this type can be deleted.
	Deletable *bool `json:"deletable,omitempty"`
	// Updateable indicates whether measurement concept classes of this type can be updated.
	Updateable *bool `json:"updateable,omitempty"`
}

// ClassMeteringLocation represents a metering location within a measurement concept class.
type ClassMeteringLocation struct {
	// ID is the universally unique identifier (UUID) of the metering location.
	ID string `json:"id"`
	// MeasurementConceptClassID is the universally unique identifier (UUID) of the measurement concept class to which the metering location is assigned.
	MeasurementConceptClassID string `json:"measurementConceptClass_id"`
	// IDText is the text describing the universally unique identifier (UUID) of the metering location.
	IDText *string `json:"idText,omitempty"`
	// ExternalCode is the external code.
	ExternalCode *string `json:"externalCode,omitempty"`
	// TypeCode is the code representing the type of metering location.
	TypeCode *string `json:"type_code,omitempty"`
	// Description is the description of the metering location.
	Description *string `json:"description,omitempty"`
	// Optional indicates whether the metering location is optional within a circuit plan.
	Optional *bool `json:"optional,omitempty"`
	// Repeatable indicates whether copies of the metering location or metering location bundle can be created during the instantiation of measurement concepts.
	Repeatable *bool `json:"repeatable,omitempty"`
	// Position is the position of the metering location.
	Position *int `json:"position,omitempty"`
}

// ClassActor represents an actor within a measurement concept class.
type ClassActor struct {
	// ID is the universally unique identifier (UUID) of the actor.
	ID string `json:"id"`
	// MeasurementConceptClassID is the universally unique identifier (UUID) of the measurement concept class to which the actor is assigned.
	MeasurementConceptClassID string `json:"measurementConceptClass_id"`
	// IDText is the text describing the universally unique identifier (UUID) of the actor.
	IDText *string `json:"idText,omitempty"`
	// ExternalCode is the external code.
	ExternalCode *string `json:"externalCode,omitempty"`
	// TypeCode is the code representing the type of actor.
	TypeCode *string `json:"type_code,omitempty"`
	// Optional indicates whether the actor is optional within a circuit plan.
	Optional *bool `json:"optional,omitempty"`
	// Repeatable indicates whether copies of the actor can be created during the instantiation of measurement concepts.
	Repeatable *bool `json:"repeatable,omitempty"`
	// DirectionCode is the code representing the direction of the actor.
	DirectionCode *string `json:"direction_code,omitempty"`
	// Position is the position of the metering location.
	Position *int `json:"position,omitempty"`
	// EnergySourceCode is the code representing the energy source of an actor.
	EnergySourceCode *string `json:"energySource_code,omitempty"`
	// PowerRangeCode is the code representing the power range of an actor.
	PowerRangeCode *string `json:"powerRange_code,omitempty"`
}

// MeasurementConceptClass represents a measurement concept class returned by the API.
type MeasurementConceptClass struct {
	// ID is the universally unique identifier (UUID) of the measurement concept class.
	ID string `json:"id"`
	// IDText is the text describing the universally unique identifier (UUID) of the measurement concept class.
	IDText *string `json:"idText,omitempty"`
	// Name is the brief description of the measurement concept class.
	Name *string `json:"name,omitempty"`
	// Description is the long description of the measurement concept class.
	Description *string `json:"description,omitempty"`
	// ClassTypeCode is the code representing the class type of the measurement concept class.
	ClassTypeCode *string `json:"classType_code,omitempty"`
	// Version is the API version.
	Version *string `json:"version,omitempty"`
	// DivisionCode is the code representing the division of the measurement concept class.
	DivisionCode *string `json:"division_code,omitempty"`
	// ClassType is the expanded class type navigation property.
	ClassType *MCClassType `json:"classType,omitempty"`
	// Division is the expanded division navigation property.
	Division *CodeNameDescription `json:"division,omitempty"`
	// MeteringLocations is the list of metering locations in this class.
	MeteringLocations []ClassMeteringLocation `json:"meteringLocations,omitempty"`
	// Actors is the list of actors in this class.
	Actors []ClassActor `json:"actors,omitempty"`
}
