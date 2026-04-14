package mcm

import "time"

// ModelMeteringProcedure represents a metering procedure assigned to a metering task
// within a measurement concept class.
type ModelMeteringProcedure struct {
	// ID is the universally unique identifier (UUID) of the metering procedure.
	ID string `json:"id"`
	// MeteringTaskID is the universally unique identifier (UUID) of the metering task.
	MeteringTaskID *string `json:"meteringTask_id,omitempty"`
	// MeteringProcedure is the expanded metering procedure type navigation property.
	MeteringProcedure *CodeNameDescription `json:"meteringProcedure,omitempty"`
	// MeteringProcedureCode is the code representing the metering procedure of a metering task.
	MeteringProcedureCode *string `json:"meteringProcedure_code,omitempty"`
	// RegisterCode is the OBIS-based register code that is determined after the installation of devices.
	RegisterCode *string `json:"registerCode,omitempty"`
}

// ModelMeteringTask represents a metering task assigned to a metering location
// within a measurement concept model.
type ModelMeteringTask struct {
	// ID is the universally unique identifier (UUID) of the metering task.
	ID string `json:"id"`
	// MeteringLocation is the expanded metering location navigation property.
	MeteringLocation *ClassMeteringLocation `json:"meteringLocation,omitempty"`
	// MeteringLocationID is the universally unique identifier (UUID) of the metering location to which the metering task is assigned.
	MeteringLocationID string `json:"meteringLocation_id"`
	// Type is the expanded metering task type navigation property.
	Type *CodeNameDescription `json:"type,omitempty"`
	// TypeCode is the code representing the metering task type.
	TypeCode *string `json:"type_code,omitempty"`
	// MeteringProcedures is the list of metering procedures for this metering task.
	MeteringProcedures []ModelMeteringProcedure `json:"meteringProcedures,omitempty"`
	// Direction is the expanded direction type navigation property.
	Direction *CodeNameDescription `json:"direction,omitempty"`
	// DirectionCode is the direction of the metering task.
	DirectionCode *string `json:"direction_code,omitempty"`
	// Position is the position of the metering task.
	Position *int `json:"position,omitempty"`
}

// ModelMarketLocationUsage represents a usage entry for a calculation rule
// in a measurement concept model.
type ModelMarketLocationUsage struct {
	// ID is the universally unique identifier (UUID) of the usage.
	ID string `json:"id"`
	// CalculationRuleID is the universally unique identifier (UUID) of the calculation rule.
	CalculationRuleID *string `json:"calculationRule_id,omitempty"`
	// Usage is the expanded usage type navigation property.
	Usage *CodeNameDescription `json:"usage,omitempty"`
	// UsageCode is the code representing the usage of the market location.
	UsageCode *string `json:"usage_code,omitempty"`
	// Position is the position of the usage.
	Position *int `json:"position,omitempty"`
}

// ModelCalculationRule represents a calculation rule that maps a formula
// to a market location in a measurement concept model.
type ModelCalculationRule struct {
	// ID is the universally unique identifier (UUID) of the calculation rule.
	ID string `json:"id"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID *string `json:"marketLocation_id,omitempty"`
	// MeteringProcedure is the expanded metering procedure type navigation property.
	MeteringProcedure *CodeNameDescription `json:"meteringProcedure,omitempty"`
	// MeteringProcedureCode is the code representing the metering procedure of a metering task.
	MeteringProcedureCode *string `json:"meteringProcedure_code,omitempty"`
	// Formula is the expanded formula navigation property.
	Formula *ModelFormula `json:"formula,omitempty"`
	// FormulaID is the universally unique identifier (UUID) of the formula.
	FormulaID *string `json:"formula_id,omitempty"`
	// RegisterCode is the OBIS-based register code that is determined after the installation of devices.
	RegisterCode *string `json:"registerCode,omitempty"`
	// Position is the position of the calculation rule.
	Position *int `json:"position,omitempty"`
	// Usages is the list of usages for this calculation rule.
	Usages []ModelMarketLocationUsage `json:"usages,omitempty"`
}

// ModelFormulaStep represents a single step in a formula calculation.
type ModelFormulaStep struct {
	// FormulaID is the universally unique identifier (UUID) of the formula.
	FormulaID string `json:"formula_id"`
	// Step is the step number in the formula.
	Step int `json:"step"`
	// Type is the type of step (e.g., variable, operator).
	Type *string `json:"type,omitempty"`
	// Value is the value used in this formula step.
	Value *string `json:"value,omitempty"`
	// Ref1 is the first reference.
	Ref1 *string `json:"ref1,omitempty"`
	// Ref2 is the second reference.
	Ref2 *string `json:"ref2,omitempty"`
	// MeteringTaskID is the universally unique identifier (UUID) of the metering task.
	MeteringTaskID *string `json:"meteringTask_id,omitempty"`
	// Operand is the variables of a formula that are mapped to metering tasks.
	Operand *string `json:"operand,omitempty"`
	// MeteringTask is the expanded metering task navigation property.
	MeteringTask *ModelMeteringTask `json:"meteringTask,omitempty"`
}

// ModelFormula represents a formula in a measurement concept model.
type ModelFormula struct {
	// ID is the universally unique identifier (UUID) of the formula.
	ID string `json:"id"`
	// IDText is the text describing the universally unique identifier (UUID) of the formula.
	IDText *string `json:"idText,omitempty"`
	// Name is the technical name or identifier of the formula.
	Name string `json:"name"`
	// Description is the detailed explanation of what the formula does.
	Description string `json:"description"`
	// IsNotUsable indicates whether the formula is currently unusable in processing logic.
	IsNotUsable bool `json:"isNotUsable"`
	// Expression is the condensed formula that expresses unsuppressed loss factors in a human-readable format.
	Expression *string `json:"expression,omitempty"`
	// Version is the version of the formula.
	Version *string `json:"version,omitempty"`
	// Position is the position of the formula.
	Position *int `json:"position,omitempty"`
	// ExpressionSubstituted is the substituted expression of the formula.
	ExpressionSubstituted *string `json:"expressionSubstituted,omitempty"`
	// FormulaSteps is the list of steps involved in the formula calculation.
	FormulaSteps []ModelFormulaStep `json:"formulaSteps,omitempty"`
}

// ModelMarketLocationActor represents an actor assigned to a market location
// in a measurement concept model.
type ModelMarketLocationActor struct {
	// ID is the universally unique identifier (UUID) of the actor.
	ID string `json:"id"`
	// MarketLocationID is the universally unique identifier (UUID) of the market location.
	MarketLocationID *string `json:"marketLocation_id,omitempty"`
	// Actor is the expanded actor navigation property.
	Actor *ClassActor `json:"actor,omitempty"`
	// ActorID is the universally unique identifier (UUID) of the actor.
	ActorID *string `json:"actor_id,omitempty"`
	// ActorIDText is the text describing the universally unique identifier (UUID) of the actor.
	ActorIDText string `json:"actorIdText"`
	// ActorDirectionCode is the code for the direction of the actor.
	ActorDirectionCode *string `json:"actorDirection_code,omitempty"`
	// ActorTypeCode is the type code of the actor.
	ActorTypeCode *string `json:"actorType_code,omitempty"`
	// Position is the position of the actor.
	Position *int `json:"position,omitempty"`
}

// ModelMarketLocation represents a market location in a measurement concept model.
type ModelMarketLocation struct {
	// ID is the universally unique identifier (UUID) of the market location.
	ID string `json:"id"`
	// MeasurementConceptModelID is the universally unique identifier (UUID) of the measurement concept model to which the market location corresponds.
	MeasurementConceptModelID *string `json:"measurementConceptModel_id,omitempty"`
	// IDText is the text describing the universally unique identifier (UUID) of the market location.
	IDText *string `json:"idText,omitempty"`
	// ExternalCode is the external code.
	ExternalCode *string `json:"externalCode,omitempty"`
	// Type is the expanded market location type navigation property.
	Type *CodeNameDescription `json:"type,omitempty"`
	// TypeCode is the code for a type of market location.
	TypeCode *string `json:"type_code,omitempty"`
	// VirtualMarketLocation indicates whether the market location is virtual.
	VirtualMarketLocation *bool `json:"virtualMarketLocation,omitempty"`
	// ActorsMapping is the list of actors assigned to this market location.
	ActorsMapping []ModelMarketLocationActor `json:"actorsMapping,omitempty"`
	// CalculationRules is the list of calculation rules for this market location.
	CalculationRules []ModelCalculationRule `json:"calculationRules,omitempty"`
	// Direction is the expanded direction type navigation property.
	Direction *CodeNameDescription `json:"direction,omitempty"`
	// DirectionCode is the code representing the direction of the market location.
	DirectionCode *string `json:"direction_code,omitempty"`
	// Position is the position of the market location.
	Position *int `json:"position,omitempty"`
}

// ModelOperandMapping represents a mapping of formula operands to metering locations
// in a measurement concept model.
type ModelOperandMapping struct {
	// ID is the universally unique identifier (UUID) of the operand mapping.
	ID string `json:"id"`
	// MeasurementConceptModelID is the universally unique identifier (UUID) of the measurement concept model to which the operand mapping corresponds.
	MeasurementConceptModelID *string `json:"measurementConceptModel_id,omitempty"`
	// Operand is the variables of a formula that are mapped to metering tasks.
	Operand *string `json:"operand,omitempty"`
	// MeteringTask is the expanded metering task navigation property.
	MeteringTask *ModelMeteringTask `json:"meteringTask,omitempty"`
	// MeteringTaskID is the universally unique identifier (UUID) of the metering task.
	MeteringTaskID *string `json:"meteringTask_id,omitempty"`
	// MeteringTaskTypeCode is the code representing the type of metering task.
	MeteringTaskTypeCode *string `json:"meteringTaskType_code,omitempty"`
	// MeteringTaskDirectionCode is the direction code of the metering task.
	MeteringTaskDirectionCode *string `json:"meteringTaskDirection_code,omitempty"`
	// MeteringLocationIDText is the text describing the universally unique identifier (UUID) of the metering location.
	MeteringLocationIDText string `json:"meteringLocationIdText"`
	// Position is the position of the operand mapping.
	Position *int `json:"position,omitempty"`
}

// ModelMeteringLocationPurpose represents a metering location purpose
// in a measurement concept model.
type ModelMeteringLocationPurpose struct {
	// ID is the universally unique identifier (UUID) of the metering location purpose.
	ID string `json:"id"`
	// MeasurementConceptModelID is the universally unique identifier (UUID) of the measurement concept model to which the metering location purpose corresponds.
	MeasurementConceptModelID *string `json:"measurementConceptModel_id,omitempty"`
	// MeteringLocationTypeCode is the code representing the type of metering location.
	MeteringLocationTypeCode *string `json:"meteringLocationType_code,omitempty"`
	// MeteringLocationIDText is the text describing the universally unique identifier (UUID) of the metering location.
	MeteringLocationIDText string `json:"meteringLocationIdText"`
	// MeteringLocation is the expanded metering location navigation property.
	MeteringLocation *ClassMeteringLocation `json:"meteringLocation,omitempty"`
	// MeteringLocationID is the universally unique identifier (UUID) of the metering location.
	MeteringLocationID *string `json:"meteringLocation_id,omitempty"`
	// Purpose is the expanded purpose type navigation property.
	Purpose *CodeNameDescription `json:"purpose,omitempty"`
	// PurposeCode is the code of the metering location purpose.
	PurposeCode *string `json:"purpose_code,omitempty"`
	// Position is the position of the metering location purpose.
	Position *int `json:"position,omitempty"`
}

// MeasurementConceptModel represents a measurement concept model returned by the API.
type MeasurementConceptModel struct {
	// ID is the universally unique identifier (UUID) of the measurement concept model.
	ID string `json:"id"`
	// ModifiedAt is the date and time at which the measurement concept model was last modified.
	ModifiedAt *time.Time `json:"modifiedAt,omitempty"`
	// CreatedAt is the date and time at which the measurement concept model was created.
	CreatedAt *time.Time `json:"createdAt,omitempty"`
	// IDText is the text describing the universally unique identifier (UUID) of the measurement concept model.
	IDText *string `json:"idText,omitempty"`
	// Name is the brief description of the measurement concept model.
	Name *string `json:"name,omitempty"`
	// Description is the long description of the measurement concept model.
	Description *string `json:"description,omitempty"`
	// ExternalCode is the external code.
	ExternalCode *string `json:"externalCode,omitempty"`
	// ConceptTypeCode is the code representing the model type of the measurement concept model.
	ConceptTypeCode *string `json:"conceptType_code,omitempty"`
	// MeasurementClassID is the universally unique identifier (UUID) of the measurement concept class.
	MeasurementClassID *string `json:"measurementClass_id,omitempty"`
	// StatusCode is the code representing the status of the measurement concept model.
	StatusCode *string `json:"status_code,omitempty"`
	// ValidFrom is the starting date of the validity period of the measurement concept model.
	ValidFrom *string `json:"validFrom,omitempty"`
	// ValidTo is the ending date of the validity period of the measurement concept model.
	ValidTo *string `json:"validTo,omitempty"`
	// DivisionCode is the code representing the division of the measurement concept model.
	DivisionCode *string `json:"division_code,omitempty"`
	// Version is the version of the measurement concept model.
	Version *string `json:"version,omitempty"`
	// ConceptType is the expanded concept type navigation property.
	ConceptType *CodeNameDescription `json:"conceptType,omitempty"`
	// MeasurementClass is the expanded measurement class navigation property.
	MeasurementClass *MeasurementConceptClass `json:"measurementClass,omitempty"`
	// Status is the expanded status navigation property.
	Status *CodeNameDescription `json:"status,omitempty"`
	// Division is the expanded division navigation property.
	Division *CodeNameDescription `json:"division,omitempty"`
	// MarketLocations is the list of market locations in this model.
	MarketLocations []ModelMarketLocation `json:"marketLocations,omitempty"`
	// ModelOperands is the list of operand mappings in this model.
	ModelOperands []ModelOperandMapping `json:"modelOperands,omitempty"`
	// MeteringLocationPurposes is the list of metering location purposes in this model.
	MeteringLocationPurposes []ModelMeteringLocationPurpose `json:"meteringLocationPurposes,omitempty"`
}
