"""Pydantic v2 models for the Measurement Concept Instance API."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from sap_mcm_client.enums import (
    ActorType,
    Direction,
    Division,
    MarketLocationUsage,
    MeteringLocationPurpose,
    MeteringLocationType,
    MeteringProcedure,
    MeteringTaskType,
    OverallStatus,
    ProcessType,
)
from sap_mcm_client.types_common import Address, MCMBaseModel, MCMRequestModel, StatusEntry
from sap_mcm_client.types_process_data import InstanceProcessData

# ---------------------------------------------------------------------------
# Frozen response models
# ---------------------------------------------------------------------------


class MarketLocationUsageEntry(MCMBaseModel):
    """A market location usage entry of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location usage.",
    )
    calculation_rule_id: UUID = Field(
        description="The universally unique identifier (UUID) of the calculation rule.",
    )
    usage_code: MarketLocationUsage | None = Field(
        None,
        max_length=12,
        description="The code representing the usage of the market location.",
    )
    position: int | None = Field(
        None,
        description="The position of the market location usage.",
    )


class CalculationRuleStep(MCMBaseModel):
    """A step within a calculation rule of a measurement concept instance."""

    calculation_rule_id: UUID = Field(
        description="The universally unique identifier (UUID) of the calculation rule.",
    )
    step: int = Field(
        description="The step of the market location.",
    )
    type: str | None = Field(
        None,
        description="The type of market location. The following types of market locations are supported: downstream grid operator, flat rate, generation market location, consumption market location, and upstream grid operator.",
    )
    value: str | None = Field(
        None,
        description="The value that is assigned to the market location step.",
    )
    ref1: int | None = Field(
        None,
        description="The first reference of the market location step.",
    )
    ref2: int | None = Field(
        None,
        description="The second reference of the market location step.",
    )
    metering_task_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering task.",
    )


class CalculationRule(MCMBaseModel):
    """A calculation rule for metering tasks of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the calculation rule.",
    )
    market_location_id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location.",
    )
    metering_procedure_code: MeteringProcedure = Field(
        max_length=3,
        description="The code representing the metering procedure of a metering task. The metering procedures ``RLM`` (interval reading) and ``SLP`` (standard load profile) are supported.",
    )
    model_calculation_rule_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model calculation rule.",
    )
    expression: str | None = Field(
        None,
        description="The condensed formula that expresses unsuppressed loss factors in a human-readable format. An expression does not contain loss functions.",
    )
    expression_expanded: str | None = Field(
        None,
        description="The expanded formula, which consists of a general formula that is augmented by loss factors and applied rules.",
    )
    planned_register_code: str | None = Field(
        None,
        alias="plannedRegisterCode",
        description="The OBIS-based register code that is planned before the installation of devices. For information about the supported codes, refer to MCIMeteringTasks.",
    )
    register_code: str | None = Field(
        None,
        alias="registerCode",
        description="The OBIS-based register code that is determined after the installation of devices. For information about the supported codes, refer to MCIMeteringTasks.",
    )
    position: int | None = Field(
        None,
        description="The position of the calculation rule.",
    )
    steps: list[CalculationRuleStep] | None = Field(
        None,
        description="The steps of the calculation rule.",
    )
    usages: list[MarketLocationUsageEntry] | None = Field(
        None,
        description="The usages of the calculation rule.",
    )


class MarketLocation(MCMBaseModel):
    """A market location of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location.",
    )
    measurement_concept_instance_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    id_text: str | None = Field(
        None,
        max_length=12,
        description="The text describing the universally unique identifier (UUID) of the market location.",
    )
    type_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the type of market location.",
    )
    direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The code for the direction of the actor.",
    )
    position: int | None = Field(
        None,
        description="The position of the market location.",
    )
    model_market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model market location.",
    )
    market_location_id: str | None = Field(
        None,
        alias="marketLocationId",
        max_length=33,
        description="The universally unique identifier (UUID) of the market location. ",
    )
    virtual_market_location: bool | None = Field(
        None,
        description="Indicates whether the market location is virtual.",
    )
    address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the address to which the market location is assigned.",
    )
    billing_procedure: str | None = Field(
        None,
        max_length=10,
        description="The metering procedure that is used for calculating the billing procedure. The value of the billing procedure is calculated from settings in the entity for market location usages.",
    )
    settlement_procedure: str | None = Field(
        None,
        max_length=10,
        description="The metering procedure that is used for calculating the settlement procedure. The value of the settlement procedure is calculated from settings in the entity for market location usages.",
    )
    removal_date: date | None = Field(
        None,
        description="The date on which the market location is removed.",
    )
    location_removed: bool | None = Field(
        None,
        description="Indicates whether the market location is removed.",
    )
    commercial_setup_date: date | None = Field(
        None,
        description="The date on which the setup activities for billing, settlement, and other commercial data processing are completed.",
    )
    location_complete: bool | None = Field(
        None,
        description="Indicates whether the setup for billing, settlement, and other commercial data processing is completed for the whole scope of the measurement concept instance.",
    )
    calculation_rules: list[CalculationRule] | None = Field(
        None,
        description="The calculation rules of the market location.",
    )


class MeteringTask(MCMBaseModel):
    """A metering task of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering task.",
    )
    metering_location_id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location.",
    )
    direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The code for the direction of the actor.",
    )
    loss_factor_transformer: Decimal | None = Field(
        None,
        description="The loss factor of the transformer.",
    )
    loss_factor_line: Decimal | None = Field(
        None,
        description="The loss factor of the line.",
    )
    type_code: MeteringTaskType | None = Field(
        None,
        max_length=12,
        description="The code representing the type of metering task.",
    )
    position: int | None = Field(
        None,
        description="The position of the metering task.",
    )
    model_metering_tasks_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model metering task.",
    )
    planned_metering_procedure_code: MeteringProcedure | None = Field(
        None,
        max_length=3,
        description="The planned metering procedure code.",
    )
    planned_register_code: str | None = Field(
        None,
        alias="plannedRegisterCode",
        description="The OBIS-based register code that is planned before the installation of devices. For information about the supported codes, refer to MCIMeteringTasks.",
    )
    register_code: str | None = Field(
        None,
        alias="registerCode",
        description="The OBIS-based register code that is determined after the installation of devices. For information about the supported codes, refer to MCIMeteringTasks.",
    )


class MeteringLocation(MCMBaseModel):
    """A metering location of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location.",
    )
    measurement_concept_instance_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    id_text: str | None = Field(
        None,
        max_length=16,
        description="The text describing the universally unique identifier (UUID) of the metering location.",
    )
    type_code: MeteringLocationType | None = Field(
        None,
        max_length=12,
        description="The code representing the type of metering location.",
    )
    position: int | None = Field(
        None,
        description="The position of the metering location.",
    )
    model_metering_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model metering location.",
    )
    metering_location_id: str | None = Field(
        None,
        alias="meteringLocationId",
        max_length=33,
        description="The universally unique identifier (UUID) of the metering location. ",
    )
    grid_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the grid of the metering location.",
    )
    grid_level_code: str | None = Field(
        None,
        max_length=10,
        description="The code representing the grid level of the metering location.",
    )
    address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the address to which the metering location is assigned.",
    )
    loss_transformer_supply: Decimal | None = Field(
        None,
        description="The transformer loss in the Supply direction.",
    )
    loss_line_supply: Decimal | None = Field(
        None,
        description="The line loss in the Supply direction.",
    )
    loss_transformer_demand: Decimal | None = Field(
        None,
        description="The transformer loss in the Demand direction.",
    )
    loss_line_demand: Decimal | None = Field(
        None,
        description="The line loss in the Demand direction.",
    )
    metering_location_purpose_code: MeteringLocationPurpose | None = Field(
        None,
        max_length=3,
        description="The code of the metering location purpose.",
    )
    disconnectable: bool | None = Field(
        None,
        description="Indicates whether the metering location can be disconnected.",
    )
    transformer_required: bool | None = Field(
        None,
        description="Indicates whether a transformer is required.",
    )
    device_serial_id: str | None = Field(
        None,
        alias="deviceSerialId",
        max_length=40,
        description="The universally unique identifier (UUID) of the device.",
    )
    removal_date: date | None = Field(
        None,
        description="The date on which the metering location is removed.",
    )
    location_removed: bool | None = Field(
        None,
        description="Indicates whether the metering location is removed.",
    )
    installation_date: date | None = Field(
        None,
        description="The date on which the metering location is installed.",
    )
    location_installed: bool | None = Field(
        None,
        description="Indicates whether the metering location is installed.",
    )
    metering_tasks: list[MeteringTask] | None = Field(
        None,
        description="The metering tasks of the metering location.",
    )


class Actor(MCMBaseModel):
    """An actor of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the actor.",
    )
    measurement_concept_instance_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    id_text: str | None = Field(
        None,
        max_length=16,
        description="The text describing the universally unique identifier (UUID) of the actor.",
    )
    type_code: ActorType | None = Field(
        None,
        max_length=12,
        description="The code representing the type of actor.",
    )
    direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The code for the direction of the actor.",
    )
    position: int | None = Field(
        None,
        description="The position of the actor.",
    )
    model_actor_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model actor.",
    )
    power_range_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the power range of an actor.",
    )
    market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the market location.",
    )
    energy_source_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the energy source of an actor. All actors belonging to the same metering location must have the same energy source. For information about the supported energy sources and their codes, refer to MCIActors.",
    )
    address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the address to which the actor is assigned.",
    )
    grid_level_code: str | None = Field(
        None,
        max_length=10,
        description="The code representing the grid level of the actor.",
    )
    is_own_consumption: bool | None = Field(
        None,
        description="Indicates whether the purpose of the metering location is for self-consumption.",
    )


class OperandMapping(MCMBaseModel):
    """Mapping of calculation rule operands to metering tasks of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the operand mapping.",
    )
    measurement_concept_instance_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
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
    position: int | None = Field(
        None,
        description="The position of the operand mapping.",
    )


class InstanceCharacteristic(MCMBaseModel):
    """A characteristic of a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the characteristic.",
    )
    change_process_id: UUID = Field(
        description="The universally unique identifier (UUID) of the change process.",
    )
    entity_type_code: str | None = Field(
        None,
        max_length=30,
        description="The code of the entity that is associated with the characteristic.",
    )
    model_entity_id: UUID | None = Field(
        None,
        alias="modelEntityId",
        description="The universally unique identifier (UUID) of the model entity.",
    )
    characteristic_code: str | None = Field(
        None,
        max_length=30,
        description="The code of the characteristic.",
    )
    value: str | None = Field(
        None,
        description="The value of the characteristic.",
    )


class ChangeProcess(MCMBaseModel):
    """A change process for a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the change process.",
    )
    measurement_concept_instance_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    external_order_id: str | None = Field(
        None,
        alias="externalOrderId",
        max_length=40,
        description="The ID of the external order that corresponds to the instantiation of the measurement concept.",
    )
    external_process_id: str | None = Field(
        None,
        alias="externalProcessId",
        max_length=40,
        description="The reference to the process ID from the pre-system.",
    )
    process_type_code: ProcessType | None = Field(
        None,
        max_length=12,
        description="The code of the process type that is involved in the change process.",
    )
    status_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the status of the change process.",
    )
    finished: bool | None = Field(
        None,
        description="Indicates whether the change process is finished.",
    )
    modified_at: datetime | None = Field(
        None,
        description="The date and time at which the change process was last modified.",
    )
    process_data: InstanceProcessData | None = Field(
        None,
        description="The process data associated with this change process.",
    )
    instance_characteristics: list[InstanceCharacteristic] | None = Field(
        None,
        description="The characteristics of the change process.",
    )


class MeasurementConceptInstance(MCMBaseModel):
    """A measurement concept instance response."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    id_text: str | None = Field(
        None,
        max_length=60,
        description="The universally unique identifier (UUID) of the text.",
    )
    version: str | None = Field(
        None,
        max_length=5,
        description="The version of the measurement concept instance.",
    )
    description: str | None = Field(
        None,
        description="The description of the measurement concept instance.",
    )
    leading_grid_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the leading grid of the measurement concept instance.",
    )
    division_code: Division | None = Field(
        None,
        max_length=2,
        description="The code representing the division of the measurement concept instance. The supported divisions are ``EL`` (electricity), ``GA`` (gas), ``WA`` (water), and ``RH`` (remote heat). The division is derived from the referenced measurement concept model and class.",
    )
    orderer_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the orderer of the measurement concept instance, who is the party who initiates the creation of the measurement concept instance. The order can be, for example, a DSO, uniquely identified by a number from the Market Master Data Register.",
    )
    leading_address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the leading address of the measurement concept instance.",
    )
    predecessor_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the preceding version of the measurement concept instance.",
    )
    difference2_predecessor_measurement_concept_instance_id: UUID | None = Field(
        None,
        alias="difference2Predecessor_measurementConceptInstance_id",
        description="The universally unique identifier (UUID) of the predecessor version of the measurement concept instance.",
    )
    measurement_model_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept model that is referenced by the measurement concept instance. To retrieve the UUID of an existing model, send a GET request to the ``/MeasurementConceptModels`` endpoint.",
    )
    measurement_class_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept class that is referenced by the measurement concept instance. To retrieve the UUID of an existing class, send a GET request to the ``/MeasurementConceptClasses`` endpoint.",
    )
    overall_status_code: OverallStatus | None = Field(
        None,
        max_length=12,
        description="The combined status of the status and the process status of the measurement concept instance. The overall statuses ``INITIAL``, ``NEW``, ``ERROR``, and ``ACTIVE`` are supported.",
    )
    status_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the status of the measurement concept instance.",
    )
    modified_at: datetime | None = Field(
        None,
        description="The date and time at which the measurement concept instance was last modified.",
    )
    modified_by: str | None = Field(
        None,
        max_length=255,
        description="The user who last modified the measurement concept instance",
    )
    installed_on: date | None = Field(
        None,
        description="The date on which the physical installation processes are completed for a version of the measurement concept instance.",
    )
    installed_until: date | None = Field(
        None,
        description="The date until a version of a measurement concept instance is valid.",
    )
    commercial_setup_on: date | None = Field(
        None,
        description="The date on which the commercial setup processes are completed for a version of a measurement concept instance.",
    )
    physical_shutdown_on: date | None = Field(
        None,
        description="The date on which the physical shutdown processes are completed for a version of a measurement concept instance.",
    )
    commercial_shutdown_on: date | None = Field(
        None,
        description="The date on which the commercial shutdown processes are completed for a version of a measurement concept instance.",
    )
    device_installations_ready: bool | None = Field(
        None,
        description="Indicates whether the metering devices are installed for the measurement concept instance.",
    )
    market_locations_complete: bool | None = Field(
        None,
        description="Indicates whether all the setup of data processing for billing and similar purposes is finished.",
    )
    metering_locations: list[MeteringLocation] | None = Field(
        None,
        description="The metering locations of the measurement concept instance.",
    )
    market_locations: list[MarketLocation] | None = Field(
        None,
        description="The market locations of the measurement concept instance.",
    )
    operand_mappings: list[OperandMapping] | None = Field(
        None,
        description="The operand mappings of the measurement concept instance.",
    )
    actors: list[Actor] | None = Field(
        None,
        description="The actors of the measurement concept instance.",
    )
    addresses: list[Address] | None = Field(
        None,
        description="The addresses of the measurement concept instance.",
    )
    change_processes: list[ChangeProcess] | None = Field(
        None,
        description="The change processes of the measurement concept instance.",
    )
    status: list[StatusEntry] | None = Field(
        None,
        description="The statuses of the measurement concept instance.",
    )


# ---------------------------------------------------------------------------
# Request / update DTOs (mutable)
# ---------------------------------------------------------------------------


class MeasurementConceptInstanceCreate(MCMRequestModel):
    """Payload for creating a measurement concept instance."""

    description: str | None = Field(
        None,
        description="The brief description of the measurement concept instance.",
    )
    measurement_model_id: UUID = Field(
        description="The universally unique identifier of the measurement concept model from which the measurement concept is instantiated.",
    )
    leading_grid_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the leading grid of the measurement concept instance.",
    )
    division_code: Division | None = Field(
        None,
        max_length=2,
        description="The code representing the division of the measurement concept instance. The supported divisions are ``EL`` (electricity), ``GA`` (gas), ``WA`` (water), and ``RH`` (remote heat). The division is derived from the referenced measurement concept model and class.",
    )
    orderer_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the orderer of the measurement concept instance, who is the party who initiates the creation of the measurement concept instance. The order can be, for example, a DSO, uniquely identified by a number from the Market Master Data Register.",
    )
    addresses: list[Address] | None = Field(
        None,
        description="The addresses of the measurement concept instance.",
    )
    change_processes: list[ChangeProcess] | None = Field(
        None,
        description="The change processes of the measurement concept instance.",
    )


class MeasurementConceptInstanceUpdate(MCMRequestModel):
    """Payload for updating a measurement concept instance."""

    leading_address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the leading address of the measurement concept instance.",
    )


class MeteringLocationUpdate(MCMRequestModel):
    """Payload for updating a metering location of a measurement concept instance."""

    grid_level_code: str | None = Field(
        None,
        max_length=10,
        description="The code representing the grid level of the metering location.",
    )
    disconnectable: bool | None = Field(
        None,
        description="Indicates whether the metering location can be disconnected.",
    )
    transformer_required: bool | None = Field(
        None,
        description="Indicates whether a transformer is required.",
    )
    installation_date: date | None = Field(
        None,
        description="The date on which the metering location is installed.",
    )
    device_serial_id: str | None = Field(
        None,
        alias="deviceSerialId",
        max_length=40,
        description="The universally unique identifier (UUID) of the device.",
    )
    metering_location_id: str | None = Field(
        None,
        alias="meteringLocationId",
        max_length=33,
        description="The universally unique identifier (UUID) of the metering location.",
    )


class MarketLocationUpdate(MCMRequestModel):
    """Payload for updating a market location of a measurement concept instance."""

    market_location_id: str | None = Field(
        None,
        alias="marketLocationId",
        max_length=33,
        description="The ID of the market location.",
    )


class ActorUpdate(MCMRequestModel):
    """Payload for updating an actor of a measurement concept instance."""

    energy_source_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the energy source of an actor. All actors belonging to the same metering location must have the same energy source. For information about the supported energy sources and their codes, refer to MCIActors.",
    )
    sub_type_code: str | None = Field(
        None,
        max_length=12,
        description="Subtype of an Actor",
    )
    installation_date: date | None = Field(
        None,
        description="The date on which an actor is installed.",
    )
    commercial_setup_date: date | None = Field(
        None,
        description="The date on which the setup activities for billing, settlement, and other commercial data processing are completed.",
    )


class MeteringTaskUpdate(MCMRequestModel):
    """Payload for updating a metering task of a measurement concept instance."""

    register_code: str | None = Field(
        None,
        alias="registerCode",
        description="The OBIS-based register code that is determined after the installation of devices. For information about the supported codes, refer to MCIMeteringTasks.",
    )


class OperandMappingUpdate(MCMRequestModel):
    """Payload for updating an operand mapping of a measurement concept instance."""

    value: str = Field(
        description="The value of the operand mapping.",
    )
