"""Common base model and shared types used across all MCM APIs.

All type definitions are derived from the SAP MCM OpenAPI specs (v1.1.0).
Field names, types, and constraints come from the specs, not from observed
API behavior. The ``extra="ignore"`` setting ensures that fields added by
SAP in future API versions will not break deserialization.

We have not validated these models against a live SAP system. If you encounter
fields or behaviors that differ from what's modeled here, please open an issue.
"""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


def _to_odata_camel(snake: str) -> str:
    """Convert snake_case to the OData wire format.

    Standard camelCase conversion, but preserves the trailing ``_suffix``
    pattern used by SAP OData for code and ID fields::

        overall_status_code  →  overallStatus_code   (not overallStatusCode)
        measurement_model_id →  measurementModel_id   (not measurementModelId)
        metering_locations_pd → meteringLocationsPD   (PD stays uppercase)
        actor_pd_id          →  actorPD_id            (PD uppercase + _suffix)
        id_text              →  idText                (normal camelCase)

    The SAP OData convention is: the last ``_segment`` stays as-is when it's
    a well-known suffix (code, id, PD). Everything before it gets camelCased.
    """
    # Known OData suffixes that must be preserved with underscore prefix
    odata_suffixes = ("_code", "_id", "_Code")

    for suffix in odata_suffixes:
        if snake.endswith(suffix) and len(snake) > len(suffix):
            prefix = snake[: -len(suffix)]
            camel_prefix = to_camel(prefix)
            return camel_prefix + suffix

    # Handle PD (process data) abbreviation: _pd at end or _pd_ in middle
    result = to_camel(snake)
    # Fix "Pd" back to "PD" — the API uses uppercase PD everywhere
    result = result.replace("Pd", "PD")
    return result


class MCMBaseModel(BaseModel):
    """Base model for all MCM entities.

    Handles snake_case (Python) to OData wire format mapping. The SAP OData API
    uses camelCase for most fields but preserves underscore suffixes for code
    and ID fields (e.g. ``division_code``, ``measurementModel_id``).

    Enforces immutability on response objects and silently ignores
    unknown fields for forward compatibility.
    """

    model_config = ConfigDict(
        alias_generator=_to_odata_camel,
        populate_by_name=True,
        frozen=True,
        extra="ignore",
    )


class CodeDescription(MCMBaseModel):
    """A reusable code-list entry returned by OData type expansions.

    Used for expanded navigation properties like classType, division,
    status, direction, etc. that all share the same {code, name, descr} pattern.
    """

    code: str = Field(description="The code value.")
    name: str | None = Field(None, max_length=255, description="The brief description of the code.")
    descr: str | None = Field(None, max_length=1000, description="The long description of the code.")


class Address(MCMBaseModel):
    """An object address associated with a measurement concept instance."""

    id: UUID = Field(description="The universally unique identifier (UUID) of the object address.")
    measurement_concept_instance_id: UUID | None = Field(
        None, description="The universally unique identifier (UUID) of the measurement concept instance."
    )
    country_code: str | None = Field(
        None, max_length=3, description="The code representing the country/region in which the measurement concept is instantiated."
    )
    city_id: str | None = Field(
        None, max_length=12, description="The city ID for which the measurement concept is instantiated."
    )
    city_name: str | None = Field(
        None, max_length=40, description="The name of the city for which the measurement concept is instantiated."
    )
    postal_code: str | None = Field(
        None, max_length=10, description="The postal code for which the measurement concept is instantiated."
    )
    city_district: str | None = Field(
        None, max_length=40, description="The city district in which the address object resides."
    )
    street_id: str | None = Field(
        None, max_length=12, description="The street ID for which the measurement concept is instantiated."
    )
    street_name: str | None = Field(
        None, max_length=60, description="The name of the street on which the measurement concept is instantiated."
    )
    house_number: str | None = Field(
        None, max_length=10, description="The number of the premise for which the measurement concept is instantiated."
    )
    house_number_supplement: str | None = Field(
        None, max_length=10, description="The number of the supplement of the address object."
    )
    floor_number: str | None = Field(
        None, description="The floor number of the premise for which the measurement concept is instantiated."
    )
    supplement: str | None = Field(None, description="The supplement of the address object.")
    latitude: Decimal | None = Field(
        None, description="The latitude of the address for which the measurement concept is instantiated."
    )
    longitude: Decimal | None = Field(
        None, description="The longitude of the address for which the measurement concept is instantiated."
    )
    time_zone: str | None = Field(
        None, max_length=32, description="The time zone in which the measurement concept is instantiated."
    )


class StatusEntry(MCMBaseModel):
    """The status of a measurement concept instance, combining instance status and process status."""

    id: UUID = Field(description="The universally unique identifier (UUID) of the status.")
    change_process_id: UUID | None = Field(
        None, description="The universally unique identifier (UUID) of the change process."
    )
    instance_status_code: str | None = Field(None, max_length=12, description="The status code of the measurement concept instance.")
    process_status_code: str | None = Field(None, max_length=30, description="The process status code of the measurement concept instance.")


class Ancestor(MCMBaseModel):
    """A reference to an ancestor (previous version) of a measurement concept instance."""

    id: UUID = Field(description="The universally unique identifier (UUID) of the ancestor instance.")
    id_text: str | None = Field(None, max_length=60, description="The human-readable identifier of the ancestor instance.")


class MCMRequestModel(BaseModel):
    """Base model for MCM request/create/update DTOs.

    Unlike ``MCMBaseModel``, this is **not** frozen and does **not** drop
    unknown fields, making it suitable for building request payloads.
    """

    model_config = ConfigDict(
        alias_generator=_to_odata_camel,
        populate_by_name=True,
    )
