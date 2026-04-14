"""Regression test: Pydantic field aliases must match Go JSON tags.

The SAP MCM OData wire format is authoritatively captured in the Go struct
tags under ``mcm/*.go`` (which in turn were cross-checked against the
OpenAPI specs under ``specs/``). This test parses those tags and verifies
that every Pydantic model in :mod:`sap_mcm_client.types_*` produces an
alias that is known to the Go side.

Without this guard, a developer adding a new Pydantic field can silently
rely on ``_to_odata_camel`` producing the wrong wire name (e.g.
``externalActor_id`` instead of ``externalActorId``), causing the field
to be dropped by ``extra="ignore"`` when the real API is called.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel

from sap_mcm_client import (
    types_actions,
    types_class,
    types_common,
    types_instance,
    types_migration,
    types_model,
    types_process_data,
    types_timeseries,
)
from sap_mcm_client.types_common import _to_odata_camel

_MCM_DIR = Path(__file__).resolve().parent.parent / "mcm"

_PYDANTIC_MODULES = (
    types_common,
    types_instance,
    types_migration,
    types_process_data,
    types_model,
    types_class,
    types_timeseries,
    types_actions,
)


def _collect_go_json_tags() -> set[str]:
    """Parse ``mcm/*.go`` (excluding tests) for every ``json:"<name>"`` tag."""
    tag_re = re.compile(r'json:"([a-zA-Z_][a-zA-Z0-9_]*)')
    tags: set[str] = set()
    for go_file in _MCM_DIR.glob("*.go"):
        if go_file.name.endswith("_test.go"):
            continue
        for match in tag_re.finditer(go_file.read_text(encoding="utf-8")):
            tags.add(match.group(1))
    return tags


def _iter_pydantic_fields() -> Iterator[tuple[str, str, str, str, str | None]]:
    """Yield ``(module, class_name, field_name, wire_name, explicit_alias)``.

    ``wire_name`` is the effective alias the Pydantic model will use
    (either the explicit ``Field(alias=...)`` if set, or the value the
    :func:`_to_odata_camel` generator produces otherwise).
    """
    for mod in _PYDANTIC_MODULES:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if not issubclass(obj, BaseModel) or obj is BaseModel:
                continue
            if obj.__module__ != mod.__name__:
                continue
            for field_name, field in obj.model_fields.items():
                explicit_alias = field.alias
                wire_name = explicit_alias or _to_odata_camel(field_name)
                yield mod.__name__, name, field_name, wire_name, explicit_alias


def test_every_pydantic_alias_is_a_go_json_tag() -> None:
    """Every effective Pydantic wire name must appear as a Go JSON tag.

    The Go structs are the ground-truth mapping of Python fields to SAP
    OData wire names. If a new Pydantic alias doesn't appear on the Go
    side, either:

    - The Go struct is missing the field (add it there), or
    - The Python alias is wrong (fix the Field(alias=...) override).
    """
    go_tags = _collect_go_json_tags()
    # Sanity check — we expect a non-trivial number of tags.
    assert len(go_tags) > 100, f"only {len(go_tags)} Go JSON tags parsed — is mcm/ empty?"

    mismatches: list[str] = []
    for module_name, class_name, field_name, wire_name, explicit_alias in _iter_pydantic_fields():
        if wire_name in go_tags:
            continue
        mismatches.append(f"{module_name}.{class_name}.{field_name} -> " f"wire={wire_name!r} alias={explicit_alias!r}")

    assert not mismatches, (
        "The following Pydantic fields produce a wire-format name that is "
        "not present in any Go JSON tag under mcm/. Either fix the Go side "
        "(if the field is missing) or add an explicit Field(alias=...) "
        "override to the Pydantic model.\n\n" + "\n".join(mismatches)
    )


def test_go_tag_extraction_finds_known_tags() -> None:
    """Sanity check on the Go tag parser — a handful of known tags must be found."""
    go_tags = _collect_go_json_tags()
    known = {
        "id",
        "idText",
        "division_code",
        "measurementModel_id",
        "registerCode",
        "plannedRegisterCode",
        "externalActorId",
        "externalOrderId",
        "externalProcessId",
        "deviceSerialId",
        "meteringLocationId",
        "marketLocationId",
        "subscriberId",
        "referenceId",
        "cityID",
        "streetID",
        "postalCode",
        "externalCode",
    }
    missing = known - go_tags
    assert not missing, f"parser failed to find expected Go tags: {sorted(missing)}"
