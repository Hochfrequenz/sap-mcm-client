"""Pydantic v2 models for the Measurement Concept Instance Migration API.

The Migration API batch-imports measurement concept instances from legacy
systems. It shares many types with the regular Instance API but has its own
endpoints and slightly different schemas — for example, ``idText`` is
required and up to 60 characters (instead of 16), metering tasks carry
``plannedMeteringProcedure_code`` instead of the instance-API
``meteringProcedure_code``, and actors gain ``subType_code``, ``interruptible``
and ``externalActorId`` fields.

All types here are derived from the SAP MCM OpenAPI spec and EDMX metadata
(v1.1.0). Field names, types, and constraints come from the specs, not from
observed API behavior.
"""

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
from sap_mcm_client.types_common import MCMBaseModel, MCMRequestModel

# ---------------------------------------------------------------------------
# Shared sub-entities (appear in both the migrate request and the response)
# ---------------------------------------------------------------------------


class MigrationAddress(MCMRequestModel):
    """An object address of a migrated measurement concept instance.

    Corresponds to ``MIGObjectAddresses`` in the OData schema. The shape matches
    :class:`~sap_mcm_client.types_common.Address` closely but is defined here
    as a request model because addresses are part of the migrate payload.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the object address.",
    )
    measurement_concept_instance_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    country_code: str | None = Field(
        None,
        max_length=3,
        description="The code representing the country/region in which the measurement concept is instantiated.",
    )
    city_id: str | None = Field(
        None,
        alias="cityID",
        max_length=12,
        description="The city ID for which the measurement concept is instantiated.",
    )
    city_name: str | None = Field(
        None,
        max_length=40,
        description="The name of the city for which the measurement concept is instantiated.",
    )
    city_district: str | None = Field(
        None,
        max_length=40,
        description="The city district in which the address object resides.",
    )
    postal_code: str | None = Field(
        None,
        alias="postalCode",
        max_length=10,
        description="The postal code for which the measurement concept is instantiated.",
    )
    street_id: str | None = Field(
        None,
        alias="streetID",
        max_length=12,
        description="The street ID for which the measurement concept is instantiated.",
    )
    street_name: str | None = Field(
        None,
        max_length=60,
        description="The name of the street on which the measurement concept is instantiated.",
    )
    house_number: str | None = Field(
        None,
        max_length=10,
        description="The number of the premise for which the measurement concept is instantiated.",
    )
    house_number_supplement: str | None = Field(
        None,
        max_length=10,
        description="The number of the supplement of the address object.",
    )
    floor_number: str | None = Field(
        None,
        description="The floor number of the premise for which the measurement concept is instantiated.",
    )
    supplement: str | None = Field(
        None,
        description="The supplement of the address object.",
    )
    latitude: Decimal | None = Field(
        None,
        description="The latitude of the address for which the measurement concept is instantiated.",
    )
    longitude: Decimal | None = Field(
        None,
        description="The longitude of the address for which the measurement concept is instantiated.",
    )
    time_zone: str | None = Field(
        None,
        max_length=32,
        description="The time zone in which the measurement concept is instantiated.",
    )


class MigrationMeteringTask(MCMRequestModel):
    """A metering task attached to a metering location during migration.

    Corresponds to ``MIGMeteringTasks``. Unlike the Instance API's
    :class:`~sap_mcm_client.types_instance.MeteringTask`, the migration variant
    exposes ``plannedMeteringProcedure_code`` and ``plannedRegisterCode``
    alongside the determined values for post-installation bookkeeping.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering task.",
    )
    metering_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering location.",
    )
    model_metering_tasks_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model metering task.",
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


class MigrationMarketLocationUsage(MCMRequestModel):
    """A market location usage entry of a migration calculation rule.

    Corresponds to ``MIGMarketLocationUsages``.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location usage.",
    )
    calculation_rule_id: UUID | None = Field(
        None,
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


class MigrationCalculationRule(MCMRequestModel):
    """A calculation rule of a migrated market location.

    Corresponds to ``MIGCalculationRules``. The migration variant omits the
    ``expressionExpanded`` and ``steps`` fields found on
    :class:`~sap_mcm_client.types_instance.CalculationRule`.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the calculation rule.",
    )
    market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the market location.",
    )
    model_calculation_rule_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model calculation rule.",
    )
    metering_procedure_code: MeteringProcedure | None = Field(
        None,
        max_length=3,
        description="The code representing the metering procedure of a metering task. The metering procedures ``RLM`` (interval reading) and ``SLP`` (standard load profile) are supported.",
    )
    expression: str | None = Field(
        None,
        description="The condensed formula that expresses unsuppressed loss factors in a human-readable format. An expression does not contain loss functions.",
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
    usages: list[MigrationMarketLocationUsage] | None = Field(
        None,
        description="The usages of the calculation rule.",
    )


class MigrationMarketLocationActor(MCMRequestModel):
    """A link between an actor and a market location in migration payloads.

    Corresponds to ``MIGMarketLocationActors``.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location actor mapping.",
    )
    actor_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the actor.",
    )
    market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the market location.",
    )
    position: int | None = Field(
        None,
        description="The position of the market location actor mapping.",
    )


class MigrationMeteringLocation(MCMRequestModel):
    """A metering location of a migrated measurement concept instance.

    Corresponds to ``MIGMeteringLocations`` (and ``InputMIGMeteringLocations``
    for the migrate request). Unlike the Instance-API metering location, this
    variant exposes ``altitude`` and omits the ``disconnectable``,
    ``locationInstalled``, ``locationRemoved``, and ``removalDate`` fields.
    ``idText`` is required and up to 60 characters long.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location.",
    )
    measurement_concept_instance_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    model_metering_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model metering location.",
    )
    id_text: str = Field(
        max_length=60,
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
    metering_location_id: str | None = Field(
        None,
        alias="meteringLocationId",
        max_length=33,
        description="The ID of the metering location.",
    )
    grid_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the grid of the metering location.",
    )
    altitude: Decimal | None = Field(
        None,
        description="The altitude of the metering location.",
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
    loss_transformer_demand: Decimal | None = Field(
        None,
        description="The transformer loss in the Demand direction.",
    )
    loss_line_demand: Decimal | None = Field(
        None,
        description="The line loss in the Demand direction.",
    )
    loss_transformer_supply: Decimal | None = Field(
        None,
        description="The transformer loss in the Supply direction.",
    )
    loss_line_supply: Decimal | None = Field(
        None,
        description="The line loss in the Supply direction.",
    )
    metering_location_purpose_code: MeteringLocationPurpose | None = Field(
        None,
        max_length=3,
        description="The code of the metering location purpose.",
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
    installation_date: date | None = Field(
        None,
        description="The date on which the metering location is installed.",
    )
    metering_tasks: list[MigrationMeteringTask] | None = Field(
        None,
        description="The metering tasks of the metering location.",
    )


class MigrationMarketLocation(MCMRequestModel):
    """A market location of a migrated measurement concept instance.

    Corresponds to ``MIGMarketLocations`` (and ``InputMIGMarketLocations`` for
    the migrate request). Unlike the Instance-API market location, this variant
    omits the ``removalDate``, ``locationRemoved`` and ``locationComplete``
    fields. ``idText`` is required and up to 60 characters long.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location.",
    )
    measurement_concept_instance_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    model_market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model market location.",
    )
    id_text: str = Field(
        max_length=60,
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
    market_location_id: str | None = Field(
        None,
        alias="marketLocationId",
        max_length=33,
        description="The ID of the market location.",
    )
    address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the address to which the market location is assigned.",
    )
    commercial_setup_date: date | None = Field(
        None,
        description="The date on which the setup activities for billing, settlement, and other commercial data processing are completed.",
    )
    virtual_market_location: bool | None = Field(
        None,
        description="Indicates whether the market location is virtual.",
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
    calculation_rules: list[MigrationCalculationRule] | None = Field(
        None,
        description="The calculation rules of the market location.",
    )
    actors_mapping: list[MigrationMarketLocationActor] | None = Field(
        None,
        description="The actor mappings of the market location.",
    )


class MigrationActor(MCMRequestModel):
    """An actor of a migrated measurement concept instance.

    Corresponds to ``MIGActors`` (and ``InputMIGActors`` for the migrate
    request). The migration variant adds ``subType_code``, ``interruptible_code``,
    ``externalActorId``, ``installationDate``, and ``commercialSetupDate``
    compared to the Instance-API :class:`~sap_mcm_client.types_instance.Actor`.
    ``idText`` is required and up to 60 characters long.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the actor.",
    )
    measurement_concept_instance_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    model_actor_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model actor.",
    )
    id_text: str = Field(
        max_length=60,
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
    power_range_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the power range of an actor.",
    )
    position: int | None = Field(
        None,
        description="The position of the actor.",
    )
    energy_source_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the energy source of an actor. All actors belonging to the same metering location must have the same energy source. For information about the supported energy sources and their codes, refer to MCIActors.",
    )
    sub_type_code: str | None = Field(
        None,
        max_length=12,
        description="The subtype of an actor.",
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
    installation_date: date | None = Field(
        None,
        description="The date on which the actor is installed.",
    )
    commercial_setup_date: date | None = Field(
        None,
        description="The date on which the setup activities for billing, settlement, and other commercial data processing are completed.",
    )
    interruptible_code: str | None = Field(
        None,
        max_length=3,
        description="The code that indicates whether and how the actor can be interrupted.",
    )
    external_actor_id: str | None = Field(
        None,
        alias="externalActorId",
        max_length=33,
        description="The external ID of the actor, used to reference the actor in legacy systems.",
    )
    market_locations: list[MigrationMarketLocationActor] | None = Field(
        None,
        description="The market location mappings of the actor.",
    )


class MigrationOperandMapping(MCMRequestModel):
    """An operand-to-metering-task mapping for a migrated instance.

    Corresponds to ``MIGOperandMappings`` (and ``InputMIGOperandMappings``).
    The input variant additionally accepts a literal ``value`` for repeatable
    operand mappings.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the operand mapping.",
    )
    measurement_concept_instance_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    operand: str | None = Field(
        None,
        max_length=60,
        description="The variables of a formula that are mapped to metering tasks.",
    )
    value: str | None = Field(
        None,
        description="The literal value assigned to a repeatable operand mapping.",
    )
    metering_task_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering task.",
    )
    position: int | None = Field(
        None,
        description="The position of the operand mapping.",
    )


class MigrationChangeProcess(MCMRequestModel):
    """A change process for a migrated measurement concept instance.

    Corresponds to ``MIGChangeProcesses`` (and ``InputMIGChangeProcesses``).
    Unlike the Instance-API change process, the migration variant does not
    carry embedded ``processData`` or ``instanceCharacteristics``.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the change process.",
    )
    measurement_concept_instance_id: UUID | None = Field(
        None,
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
        max_length=20,
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


class MigrationStatus(MCMBaseModel):
    """The status of a migrated measurement concept instance.

    Corresponds to ``MIGStatus`` — a combined view of the instance status and
    the process status after migration.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the status.",
    )
    measurement_concept_instance_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    change_process_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the change process.",
    )
    instance_status_code: str | None = Field(
        None,
        max_length=20,
        description="The status code of the measurement concept instance.",
    )
    process_status_code: str | None = Field(
        None,
        max_length=30,
        description="The process status code of the measurement concept instance.",
    )


# ---------------------------------------------------------------------------
# Migrate request body
# ---------------------------------------------------------------------------


class MigrationInstance(MCMRequestModel):
    """A single measurement concept instance to migrate.

    Corresponds to the ``MigrationInstances-migrate`` schema
    (``InputMigrationInstances`` in the EDMX metadata). Pass instances of this
    model to :meth:`~sap_mcm_client._resources.MigrationResource.migrate`.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    id_text: str = Field(
        max_length=60,
        description="The human-readable identifier of the measurement concept instance.",
    )
    version: str | None = Field(
        None,
        max_length=5,
        description="The version of the measurement concept instance.",
    )
    measurement_model_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept model from which the measurement concept is instantiated.",
    )
    measurement_class_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept class that is referenced by the measurement concept instance.",
    )
    leading_grid_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the leading grid of the measurement concept instance.",
    )
    description: str | None = Field(
        None,
        description="The description of the measurement concept instance.",
    )
    orderer_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the orderer of the measurement concept instance, who is the party who initiates the creation of the measurement concept instance.",
    )
    division_code: Division | None = Field(
        None,
        max_length=2,
        description="The code representing the division of the measurement concept instance. The supported divisions are ``EL`` (electricity), ``GA`` (gas), ``WA`` (water), and ``RH`` (remote heat).",
    )
    leading_address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the leading address of the measurement concept instance.",
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
    overwrite: bool | None = Field(
        None,
        description="If ``True``, an existing measurement concept instance with the same ID is overwritten during migration.",
    )
    addresses: list[MigrationAddress] | None = Field(
        None,
        description="The addresses of the measurement concept instance.",
    )
    change_processes: list[MigrationChangeProcess] | None = Field(
        None,
        description="The change processes of the measurement concept instance.",
    )
    metering_locations: list[MigrationMeteringLocation] | None = Field(
        None,
        description="The metering locations of the measurement concept instance.",
    )
    market_locations: list[MigrationMarketLocation] | None = Field(
        None,
        description="The market locations of the measurement concept instance.",
    )
    actors: list[MigrationActor] | None = Field(
        None,
        description="The actors of the measurement concept instance.",
    )
    operand_mappings: list[MigrationOperandMapping] | None = Field(
        None,
        description="The operand mappings of the measurement concept instance.",
    )


class MigrationInstancesRequest(MCMRequestModel):
    """Wrapper payload for the ``POST /migrate`` endpoint.

    The endpoint accepts a single JSON object with a ``migrationInstances``
    array field. This model exists primarily for callers who want to build
    the body explicitly; :meth:`~sap_mcm_client._resources.MigrationResource.migrate`
    wraps a plain list for you.
    """

    migration_instances: list[MigrationInstance] = Field(
        description="The measurement concept instances to migrate.",
    )


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------


class MigrationResponse(MCMBaseModel):
    """Response from the ``POST /migrate`` endpoint.

    The response body consists of a single ``requestId`` field that can be
    used to query the :class:`StagedMigrationInstance` collection for the
    status of the staged migration entries created by the call.
    """

    request_id: UUID = Field(
        description="The universally unique identifier (UUID) of the migration request. Use it to query the status of the staged migration instances.",
        alias="requestId",
    )


class MigrationInstanceResponse(MCMBaseModel):
    """A measurement concept instance as returned by ``GET /MigrationInstances({id})``.

    Corresponds to the ``MigrationInstance-Response`` schema (``MigrationInstances``
    in the EDMX metadata). All sub-collections are optional and only populated
    when requested via ``$expand``.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    id_text: str = Field(
        max_length=60,
        description="The human-readable identifier of the measurement concept instance.",
    )
    version: str | None = Field(
        None,
        max_length=5,
        description="The version of the measurement concept instance.",
    )
    measurement_model_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept model from which the measurement concept is instantiated.",
    )
    measurement_class_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the measurement concept class referenced by the measurement concept instance.",
    )
    leading_grid_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the leading grid of the measurement concept instance.",
    )
    description: str | None = Field(
        None,
        description="The description of the measurement concept instance.",
    )
    orderer_code: str | None = Field(
        None,
        max_length=40,
        description="The code representing the orderer of the measurement concept instance.",
    )
    division_code: Division | None = Field(
        None,
        max_length=2,
        description="The code representing the division of the measurement concept instance.",
    )
    leading_address_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the leading address of the measurement concept instance.",
    )
    installed_on: date | None = Field(
        None,
        description="The date on which the physical installation processes are completed.",
    )
    installed_until: date | None = Field(
        None,
        description="The date until a version of a measurement concept instance is valid.",
    )
    commercial_setup_on: date | None = Field(
        None,
        description="The date on which the commercial setup processes are completed.",
    )
    overall_status_code: OverallStatus | None = Field(
        None,
        max_length=20,
        description="The combined status of the instance status and the process status.",
    )
    status_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the status of the measurement concept instance.",
    )
    modified_at: datetime | None = Field(
        None,
        description="The date and time at which the measurement concept instance was last modified.",
    )
    overwrite: bool | None = Field(
        None,
        description="Indicates whether the instance was imported with the overwrite flag set.",
    )
    addresses: list[MigrationAddress] | None = Field(
        None,
        description="The addresses of the measurement concept instance.",
    )
    change_processes: list[MigrationChangeProcess] | None = Field(
        None,
        description="The change processes of the measurement concept instance.",
    )
    metering_locations: list[MigrationMeteringLocation] | None = Field(
        None,
        description="The metering locations of the measurement concept instance.",
    )
    market_locations: list[MigrationMarketLocation] | None = Field(
        None,
        description="The market locations of the measurement concept instance.",
    )
    actors: list[MigrationActor] | None = Field(
        None,
        description="The actors of the measurement concept instance.",
    )
    operand_mappings: list[MigrationOperandMapping] | None = Field(
        None,
        description="The operand mappings of the measurement concept instance.",
    )
    status: MigrationStatus | None = Field(
        None,
        description="The status of the measurement concept instance.",
    )


class StagedMigrationInstance(MCMBaseModel):
    """A single entry in the ``StagedMigrationInstances`` collection.

    Staged migration entries track the per-instance lifecycle of a migrate
    request (received → in-progress → succeeded/failed) and carry the raw
    JSON payload in ``instance_data`` until the migration completes.
    """

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the staged migration entry.",
    )
    modified_at: datetime | None = Field(
        None,
        description="The date and time at which the staged entry was last modified.",
    )
    created_at: datetime | None = Field(
        None,
        description="The date and time at which the staged entry was created.",
    )
    created_by: str | None = Field(
        None,
        max_length=255,
        description="The user who created the staged entry.",
    )
    modified_by: str | None = Field(
        None,
        max_length=255,
        description="The user who last modified the staged entry.",
    )
    request_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the migration request that produced this staged entry.",
        alias="requestId",
    )
    id_text: str = Field(
        max_length=22,
        description="The human-readable identifier of the staged migration entry.",
    )
    instance_data: str | None = Field(
        None,
        description="The raw JSON representation of the measurement concept instance to migrate.",
    )
    overwrite: bool | None = Field(
        None,
        description="Indicates whether the staged entry was submitted with the overwrite flag set.",
    )
    status_code: str | None = Field(
        None,
        max_length=12,
        description="The code for the current migration status of this staged entry.",
    )
    status_reason: str | None = Field(
        None,
        description="The reason for the current migration status of this staged entry.",
    )
    time_migration_in: datetime | None = Field(
        None,
        description="The date and time at which the staged entry was received for migration.",
    )
    time_migration_start: datetime | None = Field(
        None,
        description="The date and time at which the migration of this staged entry started.",
    )
    time_migration_end: datetime | None = Field(
        None,
        description="The date and time at which the migration of this staged entry finished.",
    )
    time_migration_duration: str | None = Field(
        None,
        max_length=16,
        description="The duration of the migration of this staged entry.",
    )
    instance_overall_status_code: OverallStatus | None = Field(
        None,
        max_length=20,
        description="The overall status of the migrated measurement concept instance.",
    )
    instance_status_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the status entry of the migrated measurement concept instance.",
    )
    instance: MigrationInstanceResponse | None = Field(
        None,
        description="The migrated measurement concept instance. Only populated when the request expands ``instance``.",
    )
