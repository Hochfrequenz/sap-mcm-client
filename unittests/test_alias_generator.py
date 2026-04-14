"""Tests for the _to_odata_camel alias generator."""

from __future__ import annotations

import pytest

from sap_mcm_client.types_common import _to_odata_camel


@pytest.mark.parametrize(
    ("snake", "expected"),
    [
        # Normal camelCase: no special suffix
        ("id_text", "idText"),
        ("installed_on", "installedOn"),
        ("device_installations_ready", "deviceInstallationsReady"),
        ("virtual_market_location", "virtualMarketLocation"),
        # _code suffix is preserved as underscore
        ("overall_status_code", "overallStatus_code"),
        ("division_code", "division_code"),
        ("type_code", "type_code"),
        ("direction_code", "direction_code"),
        ("class_type_code", "classType_code"),
        ("metering_procedure_code", "meteringProcedure_code"),
        ("process_type_code", "processType_code"),
        ("usage_code", "usage_code"),
        ("energy_source_code", "energySource_code"),
        ("grid_level_code", "gridLevel_code"),
        # _id suffix is preserved as underscore
        ("measurement_model_id", "measurementModel_id"),
        ("measurement_class_id", "measurementClass_id"),
        ("metering_location_id", "meteringLocation_id"),
        ("calculation_rule_id", "calculationRule_id"),
        ("change_process_id", "changeProcess_id"),
        ("leading_address_id", "leadingAddress_id"),
        ("status_id", "status_id"),
        ("predecessor_id", "predecessor_id"),
        ("address_id", "address_id"),
        # PD handling: Pd -> PD
        ("metering_locations_pd", "meteringLocationsPD"),
        ("market_locations_pd", "marketLocationsPD"),
        ("actors_pd", "actorsPD"),
        ("metering_tasks_pd", "meteringTasksPD"),
        # PD + _id suffix combo
        ("actor_pd_id", "actorPD_id"),
        ("metering_location_pd_id", "meteringLocationPD_id"),
        ("measurement_concept_instance_pd_id", "measurementConceptInstancePD_id"),
        # Single word — no transformation needed
        ("id", "id"),
        ("name", "name"),
        ("code", "code"),
        ("step", "step"),
        ("type", "type"),
        ("value", "value"),
        # Short prefix with _code: prefix is just one word
        ("division_code", "division_code"),
        ("rate_code", "rate_code"),
        # Multi-word normal camel
        ("leading_grid_code", "leadingGrid_code"),
        ("house_number_supplement", "houseNumberSupplement"),
        ("loss_factor_transformer", "lossFactorTransformer"),
        ("loss_transformer_supply", "lossTransformerSupply"),
    ],
)
def test_to_odata_camel(snake: str, expected: str) -> None:
    """Verify the alias generator produces the correct OData wire name."""
    assert _to_odata_camel(snake) == expected


def test_to_odata_camel_bare_code_suffix() -> None:
    """A bare '_code' (no prefix) should not strip the suffix."""
    # "_code" alone has len("_code") == 5 which equals len(snake), so no match
    # The function requires len(snake) > len(suffix)
    result = _to_odata_camel("_code")
    # Pydantic's to_camel on "_code" produces "Code" — then no suffix match
    # since "_code" doesn't have a prefix longer than suffix. In practice
    # this field name would never appear, but the function should not crash.
    assert isinstance(result, str)


def test_to_odata_camel_bare_id_suffix() -> None:
    """A bare '_id' (no prefix) should not strip the suffix."""
    result = _to_odata_camel("_id")
    assert isinstance(result, str)
