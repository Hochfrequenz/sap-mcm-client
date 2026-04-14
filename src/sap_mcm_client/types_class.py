"""Pydantic v2 models for the Measurement Concept Class API."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from sap_mcm_client.enums import ActorType, ClassType, Direction, Division, MeteringLocationType
from sap_mcm_client.types_common import CodeDescription, MCMBaseModel


class ClassMeteringLocation(MCMBaseModel):
    """A metering location within a measurement concept class."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location.",
    )
    measurement_concept_class_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept class to which the metering location is assigned.",
    )
    id_text: str | None = Field(
        None,
        max_length=12,
        description="The text describing the universally unique identifier (UUID) of the metering location.",
    )
    external_code: str | None = Field(
        None,
        alias="externalCode",
        max_length=20,
        description="The external code ",
    )
    type_code: MeteringLocationType | None = Field(
        None,
        max_length=12,
        description="The code representing the type of metering location. The supported types are ``GRIDMES`` (grid measurement), ``SERIESMES`` (serial switching measurement), ``GENERATORMES`` (generator measurement), ``STORAGEMES`` (storage measurement), ``DIFFMES`` (difference measurement), and ``COMPAREMES`` (comparative measurement).",
    )
    description: str | None = Field(
        None,
        description="The description of the metering location.",
    )
    optional: bool | None = Field(
        None,
        description="Indicates whether the metering location is optional within a circuit plan.",
    )
    repeatable: bool | None = Field(
        None,
        description="Indicates whether copies of the metering location or metering location bundle can be created during the instantiation of measurement concepts.",
    )
    position: int | None = Field(
        None,
        description="The position of the metering location.",
    )


class ClassActor(MCMBaseModel):
    """An actor within a measurement concept class."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the actor.",
    )
    measurement_concept_class_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept class to which the actor is assigned.",
    )
    id_text: str | None = Field(
        None,
        max_length=12,
        description="The text describing the universally unique identifier (UUID) of the actor.",
    )
    type_code: ActorType | None = Field(
        None,
        max_length=12,
        description="The code representing the type of actor.",
    )
    optional: bool | None = Field(
        None,
        description="Indicates whether the actor is optional within a circuit plan.",
    )
    repeatable: bool | None = Field(
        None,
        description="Indicates whether copies of the actor can be created during the instantiation of measurement concepts.",
    )
    direction_code: Direction | None = Field(
        None,
        max_length=4,
        description="The code representing the direction of the actor. The supported directions for the electricity division type are ``IN`` (supply) and ``OUT`` (demand). The supported direction for the gas, water, and remote heat division types is ``OUT`` (demand).",
    )
    position: int | None = Field(
        None,
        description="The position of the metering location.",
    )
    energy_source_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the energy source of an actor. All actors belonging to the same metering location must have the same energy source. For information about the supported energy sources and their codes, refer to MCIActors.",
    )
    power_range_code: str | None = Field(
        None,
        max_length=12,
        description="The code representing the power range of an actor.",
    )
    external_code: str | None = Field(
        None,
        alias="externalCode",
        max_length=20,
        description="The external code ",
    )


class MeasurementConceptClass(MCMBaseModel):
    """A measurement concept class response."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept class.",
    )
    id_text: str | None = Field(
        None,
        max_length=32,
        description="The text describing the universally unique identifier (UUID) of the measurement concept class.",
    )
    name: str | None = Field(
        None,
        description="The brief description of the measurement concept class.",
    )
    description: str | None = Field(
        None,
        description="The long description of the measurement concept class.",
    )
    class_type_code: ClassType | None = Field(
        None,
        max_length=12,
        description="The code representing the class type of the measurement concept class. The supported types are ``CLASS`` (class) and ``SAPTEMPLATE`` (SAP template). Classes of the SAP template type can be used only as a basis for classes of the class type, which can be used in production.",
    )
    version: str | None = Field(
        None,
        max_length=2,
        description="The API version.",
    )
    division_code: Division | None = Field(
        None,
        max_length=2,
        description="The code representing the division of the measurement concept class. The supported divisions are ``EL`` (electricity), ``GA`` (gas), ``WA`` (water), and ``RH`` (remote heat).",
    )
    class_type: CodeDescription | None = Field(
        None,
        description="The expanded class type navigation property.",
    )
    division: CodeDescription | None = Field(
        None,
        description="The expanded division navigation property.",
    )
    metering_locations: list[ClassMeteringLocation] | None = Field(
        None,
        description="The metering locations of the measurement concept class.",
    )
    actors: list[ClassActor] | None = Field(
        None,
        description="The actors of the measurement concept class.",
    )
