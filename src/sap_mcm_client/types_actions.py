"""Pydantic v2 models for measurement concept instance action requests."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import Field

from sap_mcm_client.types_common import MCMRequestModel

# ---------------------------------------------------------------------------
# Shared nested types for action requests
# ---------------------------------------------------------------------------


class _ChangeProcessData(MCMRequestModel):
    """Process data embedded in a change process for a change/init request."""

    customer_request_date: date | None = Field(
        None,
        description="The date on which a customer requests the change process for a measurement concept instance.",
    )


class _InstanceCharacteristic(MCMRequestModel):
    """A characteristic entry used in create/change action requests."""

    entity_type_code: str | None = Field(
        None,
        max_length=30,
        description="The code representing the resource from which the characteristic of the measurement concept instance originates.",
    )
    characteristic_code: str | None = Field(
        None,
        max_length=30,
        description="The code representing the characteristic of the measurement concept instance.",
    )
    model_entity_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model entity.",
    )
    value: str | None = Field(
        None,
        description="The value that is assigned to the characteristic of the measurement concept instance.",
    )


class _ChangeProcess(MCMRequestModel):
    """A change process entry embedded in a change action request."""

    external_order_id: str | None = Field(
        None,
        max_length=40,
        description="The ID of the external order that corresponds to the instantiation of the measurement concept.",
    )
    process_data: _ChangeProcessData | None = Field(
        None,
        description="The process data for the change process.",
    )
    instance_characteristics: list[_InstanceCharacteristic] | None = Field(
        None,
        description="The characteristics for the change process.",
    )


class _DataForNewInstanceVersion(MCMRequestModel):
    """The payload inside ``dataForNewInstanceVersion`` for a change action."""

    description: str | None = Field(
        None,
        description="The brief description of the changed version of measurement concept instance.",
    )
    measurement_model_id: UUID = Field(
        description="The universally unique identifier of the measurement concept model from which the measurement concept is instantiated.",
    )
    change_processes: list[_ChangeProcess] | None = Field(
        None,
        description="The change processes for the new instance version.",
    )


# ---------------------------------------------------------------------------
# Init Change
# ---------------------------------------------------------------------------


class InitChangeRequest(MCMRequestModel):
    """Request body for the ``initChange`` action on a measurement concept instance."""

    data_for_new_instance_version: list[_DataForNewInstanceVersion] = Field(
        description="The data for creating the new instance version.",
    )


# ---------------------------------------------------------------------------
# Init Merge
# ---------------------------------------------------------------------------


class _MergeAncestor(MCMRequestModel):
    """An ancestor instance to be merged."""

    id: UUID = Field(
        description="The universally unique identifier (UUID) of the measurement concept instance.",
    )
    id_text: str | None = Field(
        None,
        max_length=60,
        description="The universally unique identifier (UUID) of the text.",
    )


class _MergeInstanceCharacteristic(MCMRequestModel):
    """A characteristic entry used in merge action requests."""

    characteristic_code: str | None = Field(
        None,
        max_length=30,
        description="The code representing the characteristic of the measurement concept instance.",
    )
    model_entity_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the model entity.",
    )
    entity_type_code: str | None = Field(
        None,
        max_length=30,
        description="The code representing the resource from which the characteristic of the measurement concept instance originates.",
    )
    value: str | None = Field(
        None,
        description="The value that is assigned to the characteristic of the measurement concept instance.",
    )
    predecessor_repetition_index: str | None = Field(
        None,
        description="The code representing the resource from which the characteristic of the measurement concept instance originates.",
    )
    source_entity_id: UUID | None = Field(
        None,
        description="The universally unique identifier (UUID) of the source entity.",
    )
    source_id_text: str | None = Field(
        None,
        description="The text of the source entity identifier.",
    )
    target_id_text: str | None = Field(
        None,
        description="The text of the target entity identifier.",
    )


class _MergeProcessData(MCMRequestModel):
    """Process data embedded in a merge change process."""

    customer_request_date: date | None = Field(
        None,
        description="The date on which a customer requests the merge process for a measurement concept instance.",
    )
    leading_connection_owner: str | None = Field(
        None,
        description="The ID of the owner of the utility connection that is provided with the measurement concept instance.",
    )
    leading_connection_user: str | None = Field(
        None,
        description="The ID of the user of the utility connection that is provided with the measurement concept instance.",
    )
    note: str | None = Field(
        None,
        description="Note related to the process.",
    )
    instance_characteristics: list[_MergeInstanceCharacteristic] | None = Field(
        None,
        description="The characteristics for the merge process.",
    )


class _MergeChangeProcess(MCMRequestModel):
    """A change process entry embedded in a merge action request."""

    external_order_id: str | None = Field(
        None,
        max_length=40,
        description="The ID of the external order that corresponds to the instantiation of the measurement concept.",
    )
    process_data: _MergeProcessData | None = Field(
        None,
        description="The process data for the merge change process.",
    )


class _MergeDataForNewInstanceVersion(MCMRequestModel):
    """The payload inside ``dataForNewInstanceVersion`` for a merge action."""

    description: str | None = Field(
        None,
        description="The brief description of the mergen of measurement concept instances.",
    )
    measurement_model_id: UUID = Field(
        description="The universally unique identifier of the measurement concept model from which the measurement concept is instantiated.",
    )
    to_be_merged_ancestors: list[_MergeAncestor] = Field(
        description="The ancestor instances to be merged.",
    )
    change_processes: list[_MergeChangeProcess] = Field(
        description="The change processes for the merge.",
    )


class InitMergeRequest(MCMRequestModel):
    """Request body for the ``initMerge`` action on a measurement concept instance."""

    data_for_new_instance_version: _MergeDataForNewInstanceVersion = Field(
        description="The data for creating the merged instance version.",
    )


# ---------------------------------------------------------------------------
# Init Shutdown
# ---------------------------------------------------------------------------


class _ShutdownProcessData(MCMRequestModel):
    """Process data embedded in a shutdown change process."""

    customer_request_date: date | None = Field(
        None,
        description="The date on which a customer requests for shutdown for a measurement concept instance.",
    )


class _ShutdownChangeProcess(MCMRequestModel):
    """A change process entry embedded in a shutdown action request."""

    external_order_id: str | None = Field(
        None,
        max_length=40,
        description="The ID of the external order that corresponds to the instantiation of the measurement concept.",
    )
    process_reason_code: str | None = Field(
        None,
        max_length=20,
        description="The reason code for initiating a shutdown",
        alias="processReason_Code",
    )
    process_data: _ShutdownProcessData | None = Field(
        None,
        description="The process data for the shutdown change process.",
    )


class _ShutdownDataForNewInstanceVersion(MCMRequestModel):
    """The payload inside ``dataForNewInstanceVersion`` for a shutdown action."""

    change_processes: list[_ShutdownChangeProcess] = Field(
        description="The change processes for the shutdown.",
    )


class InitShutdownRequest(MCMRequestModel):
    """Request body for the ``initShutdown`` action on a measurement concept instance."""

    data_for_new_instance_version: list[_ShutdownDataForNewInstanceVersion] = Field(
        description="The data for creating the shutdown instance version.",
    )


# ---------------------------------------------------------------------------
# Init Version Cancel
# ---------------------------------------------------------------------------


class _VersionCancelChangeProcess(MCMRequestModel):
    """A change process entry embedded in a version cancel action request."""

    cancellation_reason: str | None = Field(
        None,
        description="The reason for cancelling the instance version.",
    )


class _VersionCancelDataForNewInstanceVersion(MCMRequestModel):
    """The payload inside ``dataForNewInstanceVersion`` for a version cancel action."""

    change_processes: list[_VersionCancelChangeProcess] | None = Field(
        None,
        description="The change processes for the version cancel.",
    )


class InitVersionCancelRequest(MCMRequestModel):
    """Request body for the ``initVersionCancel`` action on a measurement concept instance."""

    data_for_new_instance_version: _VersionCancelDataForNewInstanceVersion = Field(
        description="The data for the version cancel.",
    )
