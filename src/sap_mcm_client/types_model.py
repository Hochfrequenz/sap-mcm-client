"""Pydantic v2 models for the Measurement Concept Model API."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from sap_mcm_client.enums import (
    ActorType,
    ConceptType,
    Direction,
    Division,
    MarketLocationUsage,
    MeteringLocationType,
    MeteringLocationPurpose,
    MeteringProcedure,
    MeteringTaskType,
    ModelStatus,
)
from sap_mcm_client.types_class import MeasurementConceptClass
from sap_mcm_client.types_common import CodeDescription, MCMBaseModel


class ModelMeteringTask(MCMBaseModel):
    """A metering task within a measurement concept model."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering task.",
    )
    metering_location_id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location to which the metering task is assigned. ",
    )
    type: CodeDescription | None = Field(
        None,
        description="The expanded metering task type navigation property.",
    )
    type_code: MeteringTaskType | None = Field(
        None,
        max_length=12,
        description="The code representing the metering task type. The supported types are ``AE`` (active energy), ``OV`` (operating volume), and ``EV`` (energetic value). For division-specific information about these types, refer to MCIMeteringTasks.",
    )
    metering_procedures: list[ModelMeteringProcedure] | None = Field(
        None,
        description="The metering procedures of the metering task.",
    )
    direction: CodeDescription | None = Field(
        None,
        description="The expanded direction navigation property.",
    )
    direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The direction of the metering task. The direction can be ``IN`` (energy that feeds into a grid) or ``OUT`` (energy that is consumed from a grid). The direction is derived from the measurement concept model.",
    )
    position: int | None = Field(
        None,
        description="The position of the metering task.",
    )


class ModelMeteringProcedure(MCMBaseModel):
    """A metering procedure within a measurement concept model."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering procedure.",
    )
    metering_task_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering task.",
    )
    metering_procedure: CodeDescription | None = Field(
        None,
        description="The expanded metering procedure navigation property.",
    )
    metering_procedure_code: MeteringProcedure | None = Field(
        None,
        max_length=3,
        description="The code representing the metering procedure of a metering task. The metering procedures ``RLM`` (interval reading) and ``SLP`` (standard load profile) are supported.",
    )
    register_code: str | None = Field(
        None,
        description="The OBIS-based register code that is determined after the installation of devices. For information about the supported codes, refer to MCIMeteringTasks.",
    )


class ModelMarketLocationUsage(MCMBaseModel):
    """A market location usage within a calculation rule."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the usage.",
    )
    calculation_rule_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the calculation rule.",
    )
    usage: CodeDescription | None = Field(
        None,
        description="The expanded usage navigation property.",
    )
    usage_code: MarketLocationUsage | None = Field(
        None,
        max_length=12,
        description="The code representing the usage of the market location.",
    )
    position: int | None = Field(
        None,
        description="The position of the usage.",
    )


class ModelCalculationRule(MCMBaseModel):
    """A calculation rule mapping formulas to market locations."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the calculation rule.",
    )
    market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the market location.",
    )
    metering_procedure: CodeDescription | None = Field(
        None,
        description="The expanded metering procedure navigation property.",
    )
    metering_procedure_code: MeteringProcedure | None = Field(
        None,
        max_length=3,
        description="The code representing the metering procedure of a metering task. The metering procedures ``RLM`` (interval reading) and ``SLP`` (standard load profile) are supported.",
    )
    formula: ModelFormula | None = Field(
        None,
        description="The expanded formula navigation property.",
    )
    formula_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the formula.",
    )
    register_code: str | None = Field(
        None,
        description="The OBIS-based register code that is determined after the installation of devices. For information about the supported codes, refer to MCIMeteringTasks.",
    )
    position: int | None = Field(
        None,
        description="The position of the calculation rule.",
    )
    usages: list[ModelMarketLocationUsage] | None = Field(
        None,
        description="The usages of the calculation rule.",
    )


class ModelFormulaStep(MCMBaseModel):
    """A single step in a formula calculation."""

    formula_id: UUID = Field(
        description="The universally unique identifier (UUID) of the formula.",
    )
    step: int = Field(
        description="The step number.",
    )
    type: str | None = Field(
        None,
        description="The type of step (e.g., variable, operator).",
    )
    value: str | None = Field(
        None,
        description="The value used in this formula step.",
    )
    ref1: str | None = Field(
        None,
        description="The first reference.",
    )
    ref2: str | None = Field(
        None,
        description="The second reference.",
    )
    metering_task_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering task.",
    )
    operand: str | None = Field(
        None,
        max_length=12,
        description="The variables of a formula that are mapped to metering tasks.",
    )


class ModelFormula(MCMBaseModel):
    """A formula of a measurement concept model."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the formula.",
    )
    id_text: str | None = Field(
        None,
        max_length=32,
        description="The text describing the universally unique identifier (UUID) of the formula.",
    )
    name: str | None = Field(
        None,
        description="Technical name or identifier of the formula, typically used internally for referencing.",
    )
    description: str | None = Field(
        None,
        description="Detailed explanation of what the formula does, including its purpose or calculation logic if applicable.",
    )
    is_not_usable: bool | None = Field(
        None,
        description="Indicates whether the formula is currently unusable in processing logic.",
    )
    expression: str | None = Field(
        None,
        description="The condensed formula that expresses unsuppressed loss factors in a human-readable format. An expression does not contain loss functions.",
    )
    version: str | None = Field(
        None,
        max_length=5,
        description="The version of the formula.",
    )
    position: int | None = Field(
        None,
        description="The position of the formula.",
    )
    expression_substituted: str | None = Field(
        None,
        description="The substituted expression of the formula.",
    )
    formula_steps: list[ModelFormulaStep] | None = Field(
        None,
        description="The steps involved in the formula calculation.",
    )


class ModelMarketLocationActor(MCMBaseModel):
    """An actor mapped to a market location."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the actor.",
    )
    market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the market location.",
    )
    actor_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the actor.",
    )
    actor_id_text: str | None = Field(
        None,
        max_length=16,
        description="The text describing the universally unique identifier (UUID) of the actor.",
    )
    actor_direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The code for the direction of the actor.",
    )
    actor_type_code: ActorType | None = Field(
        None,
        max_length=12,
        description="The type code of the actor.",
    )
    position: int | None = Field(
        None,
        description="The position of the actor.",
    )


class ModelMarketLocation(MCMBaseModel):
    """A market location within a measurement concept model."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location.",
    )
    measurement_concept_model_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept model to which the market location corresponds.",
    )
    id_text: str | None = Field(
        None,
        max_length=12,
        description="The text describing the universally unique identifier (UUID) of the market location.",
    )
    external_code: str | None = Field(
        None,
        max_length=20,
        description="The external code.",
    )
    type: CodeDescription | None = Field(
        None,
        description="The expanded market location type navigation property.",
    )
    type_code: str | None = Field(
        None,
        max_length=12,
        description="The code for a type of market location.",
    )
    virtual_market_location: bool | None = Field(
        None,
        description="Indicates whether the market location is virtual.",
    )
    actors_mapping: list[ModelMarketLocationActor] | None = Field(
        None,
        description="The actors mapped to the market location.",
    )
    calculation_rules: list[ModelCalculationRule] | None = Field(
        None,
        description="The calculation rules of the market location.",
    )
    direction: CodeDescription | None = Field(
        None,
        description="The expanded direction navigation property.",
    )
    direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The code representing the direction of the market location. The supported directions for the electricity division type are ``IN`` (supply) and ``OUT`` (demand). The supported direction for the gas, water, and remote heat division types is ``OUT`` (demand).",
    )
    position: int | None = Field(
        None,
        description="The position of the market location.",
    )


class ModelOperandMapping(MCMBaseModel):
    """Mapping of formula operands to metering locations."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the operand mapping.",
    )
    measurement_concept_model_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept model to which the operand mapping corresponds.",
    )
    operand: str | None = Field(
        None,
        max_length=12,
        description="The variables of a formula that are mapped to metering tasks.",
    )
    metering_task_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering task.",
    )
    metering_task_type_code: MeteringTaskType | None = Field(
        None,
        max_length=12,
        description="The code representing the type of metering task.",
    )
    metering_task_direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The direction code of the metering task.",
    )
    metering_location_id_text: str | None = Field(
        None,
        max_length=16,
        description="The text describing the universally unique identifier (UUID) of the metering location.",
    )
    position: int | None = Field(
        None,
        description="The position of the operand mapping.",
    )


class ModelMeteringLocationPurpose(MCMBaseModel):
    """A metering location purpose within a measurement concept model."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location purpose.",
    )
    measurement_concept_model_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept model to which the metering location purpose corresponds.",
    )
    metering_location_type_code: MeteringLocationType | None = Field(
        None,
        max_length=12,
        description="The code representing the type of metering Location.",
    )
    metering_location_id_text: str | None = Field(
        None,
        max_length=16,
        description="The text describing the universally unique identifier (UUID) of the metering location.",
    )
    metering_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering location.",
    )
    purpose: CodeDescription | None = Field(
        None,
        description="The expanded purpose navigation property.",
    )
    purpose_code: MeteringLocationPurpose | None = Field(
        None,
        max_length=3,
        description="The code of the metering location purpose. The purposes ``SC`` (self-consumption) and ``CST`` (commercial settlement transfer) are supported.",
    )
    position: int | None = Field(
        None,
        description="The position of the metering location purpose.",
    )


class MeasurementConceptModel(MCMBaseModel):
    """A measurement concept model response."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept model.",
    )
    modified_at: datetime | None = Field(
        None,
        description="The date and time at which the measurement concept model was last modified.",
    )
    created_at: datetime | None = Field(
        None,
        description="The date and time at which the measurement concept model was created.",
    )
    id_text: str | None = Field(
        None,
        max_length=32,
        description="The text describing the universally unique identifier (UUID) of the measurement concept model.",
    )
    name: str | None = Field(
        None,
        description="The brief description of the measurement concept model.",
    )
    description: str | None = Field(
        None,
        description="The long description of the measurement concept model.",
    )
    external_code: str | None = Field(
        None,
        max_length=20,
        description="The external code.",
    )
    concept_type_code: ConceptType | None = Field(
        None,
        max_length=12,
        description="The code representing the model type of the measurement concept model. The supported types are ``MODEL`` (model) and ``SAPTEMPLATE`` (SAP template). Models of the SAP template type can be used only as a basis for models of the model type, which can be used in production.",
    )
    measurement_class_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept class.",
    )
    status_code: ModelStatus | None = Field(
        None,
        max_length=12,
        description="The code representing the status of the measurement concept model. The supported status are ``IN_PROGRESS`` (in progress), ``ACTIVE`` (active), and ``DEACTIVATED`` (deactivated).",
    )
    valid_from: date | None = Field(
        None,
        description="The starting date of the validity period of the measurement concept model.",
    )
    valid_to: date | None = Field(
        None,
        description="The ending date of the validity period of the measurement concept model.",
    )
    division_code: Division | None = Field(
        None,
        max_length=2,
        description="The code representing the division of the measurement concept model. The supported divisions are ``EL`` (electricity), ``GA`` (gas), ``WA`` (water), and ``RH`` (remote heat).",
    )
    version: str | None = Field(
        None,
        max_length=5,
        description="The version of the measurement concept model.",
    )
    concept_type: CodeDescription | None = Field(
        None,
        description="The expanded concept type navigation property.",
    )
    status: CodeDescription | None = Field(
        None,
        description="The expanded status navigation property.",
    )
    division: CodeDescription | None = Field(
        None,
        description="The expanded division navigation property.",
    )
    market_locations: list[ModelMarketLocation] | None = Field(
        None,
        description="The market locations of the measurement concept model.",
    )
    model_operands: list[ModelOperandMapping] | None = Field(
        None,
        description="The operand mappings of the measurement concept model.",
    )
    measurement_class: MeasurementConceptClass | None = Field(
        None,
        description="The measurement concept class referenced by this model.",
    )
    metering_location_purposes: list[ModelMeteringLocationPurpose] | None = Field(
        None,
        description="The metering location purposes of the measurement concept model.",
    )


# Rebuild forward references so ModelMeteringTask can reference ModelMeteringProcedure
ModelMeteringTask.model_rebuild()
ModelCalculationRule.model_rebuild()
