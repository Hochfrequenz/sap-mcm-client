"""Pydantic v2 models for the SAP MCM Time Series API.

All type definitions are derived from the SAP Time Series OpenAPI spec
(``specs/time-series.json``). Field names, types, and constraints come
from the spec, not from observed API behavior.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, model_validator

from sap_mcm_client.types_common import MCMBaseModel, MCMRequestModel


class TimeSeriesDataPoint(MCMBaseModel):
    """A single time series data point.

    The Time Series API spec defines two response schemas —
    ``TimeSeriesDataExtended`` (current data) and
    ``TimeSeriesDataHistoryValues`` (historical data) — with identical
    structure. This unified type represents both.
    """

    id: str = Field(
        description="The identifier of the time series data point record.",
        alias="ID",
    )
    import_id: str | None = Field(
        None,
        description="The identifier of the import batch that produced this data point.",
        alias="importID",
    )
    timestamp: datetime | None = Field(
        None,
        description="The timestamp to which the data point applies.",
    )
    time_zone_code: str | None = Field(
        None,
        description="The time zone code associated with the timestamp.",
        alias="timeZoneCode",
    )
    created_at: datetime | None = Field(
        None,
        description="The date and time at which the data point record was created.",
    )
    value: Decimal | None = Field(
        None,
        description="The measured or calculated value at the given timestamp. May be null when the value is missing.",
    )
    missing: bool | None = Field(
        None,
        description="Indicates whether the data point's value is missing.",
    )
    quality: str | None = Field(
        None,
        description="The quality indicator for the data point.",
    )
    time_series_id: str | None = Field(
        None,
        description="The universally unique identifier (UUID) of the time series to which the data point belongs.",
        alias="timeSeriesID",
    )
    external_id: str | None = Field(
        None,
        description="The external identifier of the time series to which the data point belongs.",
        alias="externalID",
    )


class DeleteTimeSeriesRequest(MCMRequestModel):
    """Request body for the Time Series bulk delete endpoint.

    At least one of ``uuids`` or ``external_ids`` must be provided.
    The server enforces a maximum of 100 identifiers per request and a
    maximum range of one year between ``start_time`` and ``end_time``.
    """

    uuids: list[UUID] | None = Field(
        None,
        description="List of time series UUIDs that are to be deleted.",
    )
    external_ids: list[str] | None = Field(
        None,
        description="List of externalIDs that are to be deleted.",
    )
    start_time: datetime = Field(
        description="Start timestamp for deletion.",
    )
    end_time: datetime = Field(
        description="End timestamp for deletion.",
    )

    @model_validator(mode="after")
    def _validate_identifiers(self) -> DeleteTimeSeriesRequest:
        """Require at least one identifier collection to be non-empty."""
        if not self.uuids and not self.external_ids:
            raise ValueError("DeleteTimeSeriesRequest requires at least one of 'uuids' or 'external_ids'.")
        return self
