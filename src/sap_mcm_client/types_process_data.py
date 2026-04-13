"""Pydantic v2 models for measurement concept instance process data."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from sap_mcm_client.enums import ForecastBasis, MeasuringType, Rate
from sap_mcm_client.types_common import MCMBaseModel, MCMRequestModel


# ---------------------------------------------------------------------------
# Frozen response models
# ---------------------------------------------------------------------------


class ActorPDExternalReference(MCMBaseModel):
    """An external reference of process data for an actor."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the external reference.",
    )
    modified_at: datetime | None = Field(
        None,
        description="The date and time at which the external reference was last modified.",
    )
    created_at: datetime | None = Field(
        None,
        description="The date and time at which the external reference was created.",
    )
    created_by: str | None = Field(
        None,
        max_length=255,
        description="The user who created the external reference.",
    )
    modified_by: str | None = Field(
        None,
        max_length=255,
        description="The user who last modified the external reference.",
    )
    created_by_uuid: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the user who created the external reference.",
    )
    modified_by_uuid: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the user who last modified the external reference.",
    )
    actor_pd_id: UUID = Field(
        description="The universally unique identifier (UUID) of the actor.",
    )
    reference_type_code: str | None = Field(
        None,
        max_length=12,
        description="The code for the type of external reference.",
    )
    reference_system_code: str | None = Field(
        None,
        max_length=20,
        description="The code for the system wherein the reference is stored.",
    )
    reference_id: str | None = Field(
        None,
        description="The ID of the external reference.",
    )
    position: int | None = Field(
        None,
        description="The position of the external reference.",
    )


class ActorPD(MCMBaseModel):
    """Process data of an actor for a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the actor.",
    )
    measurement_concept_instance_pd_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    actor_id: UUID = Field(
        description="The universally unique identifier (UUID) of the actor",
    )
    position: int | None = Field(
        None,
        description="The position of the actor.",
    )
    planned_installed_power: Decimal | None = Field(
        None,
        description="The planned installed power of the actor. The planned installed power can be between ``0`` and ``100,000`` kW, including decimals.",
    )
    installed_power: Decimal | None = Field(
        None,
        description="The installed power of the actor. The installed power can be between ``0`` and ``100,000`` kW, including decimals.",
    )
    inverter_power: Decimal | None = Field(
        None,
        description="The inverter power of the actor. The inverter power can be between ``0`` and ``100,000`` kW, including decimals.",
    )
    external_references: list[ActorPDExternalReference] | None = Field(
        None,
        description="The external references of the actor.",
    )


class MeteringTaskPD(MCMBaseModel):
    """Process data of a metering task for a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering task.",
    )
    metering_location_pd_id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location to which the metering task is assigned.",
    )
    metering_task_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering task.",
    )
    position: int | None = Field(
        None,
        description="The position of the metering task.",
    )
    rate_code: Rate | None = Field(
        None,
        max_length=10,
        description="The tariff code of the metering task. The tariffs ``SR`` (single rate) and ``DR`` (double rate) are supported.",
    )
    period_consumption: Decimal | None = Field(
        None,
        description="The consumption over a one-year period provided as a positive value in kWh.",
    )


class MeteringLocationPD(MCMBaseModel):
    """Process data of a metering location for a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the metering location.",
    )
    measurement_concept_instance_pd_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    metering_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the metering location.",
    )
    position: int | None = Field(
        None,
        description="The position of the metering location.",
    )
    planned_metering_location_id: str | None = Field(
        None,
        max_length=33,
        description="The ID of a customer's own metering location.",
    )
    device_location_supplement: str | None = Field(
        None,
        max_length=60,
        description="The supplementary information about the location of a device, acting as a hint for electricians.",
    )
    meter_operator: str | None = Field(
        None,
        description="The unique identifier (ILN) of the meter operator.",
    )
    note: str | None = Field(
        None,
        description="The user-provided information about the metering location.",
    )
    classification: str | None = Field(
        None,
        description="The classification of the metering location such as household, streetlight, shop, and restuarant.",
    )
    measuring_type_code: MeasuringType | None = Field(
        None,
        max_length=12,
        description="The code for the type of measuring device. The measuring types ``CME`` (conventional meter), ``MME`` (modern meter), ``iMS`` (smart meter), and ``NoMeasuring`` (no meter) are supported.",
    )
    volume_corrector: bool | None = Field(
        None,
        description="Indicates whether the volume corrector is set.",
    )
    nominal_capacity: Decimal | None = Field(
        None,
        description="The nominal capacity of the metering location.",
    )
    location_identifier_ready: bool | None = Field(
        None,
        description="Indicates whether the completion of settings point of delivery IDs can be signaled.",
    )
    master_data_ready: bool | None = Field(
        None,
        description="Indicates whether all parameters related to master data readiness are set to ``True``.",
    )
    calorific_value_district: str | None = Field(
        None,
        max_length=10,
        description="The calorific value district of the metering location that is used in the gas division.",
    )
    installation_date: date | None = Field(
        None,
        description="The date on which the metering location is installed. The value is passed over from GM through SAP S/4HANA Utilities.",
    )
    location_installed: bool | None = Field(
        None,
        description="Indicates whether the metering location is installed.",
    )
    removal_date: date | None = Field(
        None,
        description="The date on which the metering location is removed.",
    )
    location_removed: bool | None = Field(
        None,
        description="Indicates whether the metering location is removed.",
    )
    metering_tasks_pd: list[MeteringTaskPD] | None = Field(
        None,
        description="The process data of the metering tasks.",
    )


class MarketLocationPD(MCMBaseModel):
    """Process data of a market location for a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the market location.",
    )
    measurement_concept_instance_pd_id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    market_location_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the market location.",
    )
    position: int | None = Field(
        None,
        description="The position of the market location.",
    )
    connection_user: str | None = Field(
        None,
        description="The ID of the user of the utility connection that is provided with the measurement concept instance.",
    )
    connection_owner: str | None = Field(
        None,
        description="The ID of the owner of the utility connection that is provided with the measurement concept instance.",
    )
    forecast_basis_code: ForecastBasis | None = Field(
        None,
        max_length=12,
        description="The code of the forecast basis of the market location. The forecast bases ``RLM``, ``REM``, and ``HO`` are supported.",
    )
    consumption_distribution: str | None = Field(
        None,
        description="The consumption distribution of the market location. This is, for example, temperature-dependent.",
    )
    flatrate_type_code: str | None = Field(
        None,
        max_length=12,
        description="The code of the type of flat rate.",
    )
    flatrate: str | None = Field(
        None,
        description="The flat rate of the market location. This parameter is mandatory for market locations of the type ``FLATRATE``.",
    )
    classification: str | None = Field(
        None,
        description="The classification of a market location such as household, streetlight, shop, and restaurant.",
    )
    direct_selling: bool | None = Field(
        None,
        description="Indicates whether the market location supports direct selling.",
    )
    connection_operator: str | None = Field(
        None,
        description="The operator of the connection of the market location. The value of this parameter must not be null if there is at least one actor of type ``PRODUCER`` that is assigned to the market location.",
    )
    location_identifier_ready: bool | None = Field(
        None,
        description="Indicates whether the completion of settings point of delivery IDs can be signaled.",
    )
    master_data_ready: bool | None = Field(
        None,
        description="Indicates whether all parameters related to master data readiness are set to ``True``.",
    )
    commercial_setup_date: date | None = Field(
        None,
        description="The date on which the setup activities for billing, settlement, and other commercial data processing are completed.",
    )
    location_complete: bool | None = Field(
        None,
        description="Indicates whether the setup for billing, settlement, and other commercial data processing is completed for the entire scope of the measurement concept instance.",
    )
    location_removed: bool | None = Field(
        None,
        description="Indicates whether the market location is removed.",
    )
    removal_date: date | None = Field(
        None,
        description="The date on which the market location is removed.",
    )
    communal_installation: bool | None = Field(
        None,
        description="The communal installation of the market location.",
    )


class InstanceProcessData(MCMBaseModel):
    """Process data for a measurement concept instance."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the process data of the measurement concept instance.",
    )
    change_process_id: UUID = Field(
        description="The universally unique identifier (UUID) of the change process.",
    )
    subscriber_id: str | None = Field(
        None,
        description="The ID of the subscriber.",
    )
    leading_connection_user: str | None = Field(
        None,
        description="The ID of the user of the utility connection that is provided with the measurement concept instance.",
    )
    leading_connection_owner: str | None = Field(
        None,
        description="The ID of the owner of the utility connection that is provided with the measurement concept instance.",
    )
    note: str | None = Field(
        None,
        description="The user-provided information about the measurement concept instance.",
    )
    initial_data_entry_ready: bool | None = Field(
        None,
        description="Indicates whether a pre-system (for example, the DSO) is enabled to notify the measurement concept management component about the readiness of DSO's first data entry for a measurement concept instance.",
    )
    location_identifiers_ready: bool | None = Field(
        None,
        description="Indicates whether the completion of settings point of delivery IDs can be signaled",
    )
    final_data_entry_ready: bool | None = Field(
        None,
        description="Indicates whether the point of delivery IDs are known for each location and that interested parties can read those IDs to continue and distribute the point of delivery IDs in their process and data.",
    )
    master_data_ready: bool | None = Field(
        None,
        description="Indicates whether all parameters related to master data readiness are set to ``True``.",
    )
    device_installations_ready: bool | None = Field(
        None,
        description="Indicates whether all devices were installed at physical locations corresponding to the metering locations and that relevant data is set.",
    )
    market_locations_complete: bool | None = Field(
        None,
        description="Indicates whether all the setup for billing, settlement, and other commercial data processing is completed for the entire scope of the measurement concept instance.",
    )
    metering_locations_pd: list[MeteringLocationPD] | None = Field(
        None,
        description="The process data of the metering locations.",
    )
    market_locations_pd: list[MarketLocationPD] | None = Field(
        None,
        description="The process data of the market locations.",
    )
    actors_pd: list[ActorPD] | None = Field(
        None,
        description="The process data of the actors.",
    )


# ---------------------------------------------------------------------------
# Update DTOs (mutable)
# ---------------------------------------------------------------------------


class MeteringLocationPDUpdate(MCMRequestModel):
    """Payload for updating metering location process data."""

    classification: str | None = Field(
        None,
        description="The classification of the metering location such as household, streetlight, shop, and restuarant.",
    )
    note: str | None = Field(
        None,
        description="The user-provided information about the metering location.",
    )
    volume_corrector: bool | None = Field(
        None,
        description="Indicates whether the volume corrector is set.",
    )
    meter_operator: str | None = Field(
        None,
        description="The unique identifier (ILN) of the meter operator.",
    )
    nominal_capacity: Decimal | None = Field(
        None,
        description="The nominal capacity of the metering location.",
    )
    measuring_type_code: MeasuringType | None = Field(
        None,
        max_length=12,
        description="The code for the type of measuring device. The measuring types ``CME`` (conventional meter), ``MME`` (modern meter), ``iMS`` (smart meter), and ``NoMeasuring`` (no meter) are supported.",
    )
    location_code: str | None = Field(
        None,
        max_length=10,
        description="Location code for metering location.",
    )


class MeteringTaskPDUpdate(MCMRequestModel):
    """Payload for updating metering task process data."""

    rate_code: Rate | None = Field(
        None,
        max_length=10,
        description="The tariff code of the metering task. The tariffs ``SR`` (single rate) and ``DR`` (double rate) are supported.",
    )
    period_consumption: Decimal | None = Field(
        None,
        description="The consumption over a one-year period provided as a positive value in kWh.",
    )


class MarketLocationPDUpdate(MCMRequestModel):
    """Payload for updating market location process data."""

    classification: str | None = Field(
        None,
        description="The classification of the market location such as household, streetlight, shop, and restaurant.",
    )
    connection_user: str | None = Field(
        None,
        description="The ID of the user of the utility connection that is provided with the measurement concept instance.",
    )
    connection_owner: str | None = Field(
        None,
        description="The ID of the owner of the utility connection that is provided with the measurement concept instance.",
    )
    forecast_basis_code: ForecastBasis | None = Field(
        None,
        max_length=12,
        description="The code of the forecast basis of the market location. The forecast bases ``RLM``, ``REM``, and ``HO`` are supported.",
    )
    consumption_distribution: str | None = Field(
        None,
        description="The consumption distribution of the market location. This is, for example, temperature-dependent.",
    )
    commercial_setup_date: date | None = Field(
        None,
        description="The date on which the setup activities for billing, settlement, and other commercial data processing are completed.",
    )
