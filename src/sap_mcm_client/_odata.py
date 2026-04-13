"""OData V4 protocol helpers for the SAP MCM client.

This module encapsulates all OData-specific logic — header conventions,
``$expand`` / ``$filter`` / ``$orderby`` query parameter construction, and
response envelope parsing — so that the public client surface stays clean.

The ``INCLUDE_EXPAND_MAP`` dictionaries document which OData navigation
properties each API endpoint supports. These mappings are derived from the
SAP MCM OpenAPI specs (v1.1.0) and may need updating if SAP changes the API
in future versions. We have not validated every combination against a live
system; if you find a mismatch, please open an issue.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sap_mcm_client.types_common import MCMBaseModel, _to_odata_camel

T = TypeVar("T", bound=MCMBaseModel)

# ---------------------------------------------------------------------------
# OData wire-format constants
# ---------------------------------------------------------------------------

ODATA_HEADERS: dict[str, str] = {
    "Accept": "application/json;odata.metadata=minimal;IEEE754Compatible=true",
    "Content-Type": "application/json;charset=UTF-8;IEEE754Compatible=true",
}
"""Default HTTP headers for every OData V4 request.

``IEEE754Compatible=true`` tells the server to serialise ``Edm.Decimal`` and
``Edm.Int64`` as JSON strings so that no precision is lost on the wire.
"""

# ---------------------------------------------------------------------------
# $expand maps — one per API endpoint
# ---------------------------------------------------------------------------

INSTANCE_EXPAND_MAP: dict[str, str | None] = {
    "metering_locations": "meteringLocations($expand=meteringTasks)",
    "market_locations": "marketLocations($expand=calculationRules($expand=steps,usages))",
    "actors": "actors",
    "addresses": "addresses",
    "operand_mappings": "operandMappings",
    "change_processes": (
        "changeProcesses("
        "$expand=processData("
        "$expand=meteringLocationsPD($expand=meteringTasksPD),"
        "marketLocationsPD,"
        "actorsPD($expand=externalReferences)"
        "),instanceCharacteristics"
        ")"
    ),
    "status": "status",
    "all": None,  # sentinel: expand everything via $expand=*
}
"""User-friendly include names mapped to OData ``$expand`` fragments for
the Measurement Concept Instance endpoint."""

CLASS_EXPAND_MAP: dict[str, str | None] = {
    "metering_locations": "meteringLocations",
    "actors": "actors",
    "class_type": "classType",
    "division": "division",
    "all": None,
}
"""``$expand`` map for the Measurement Concept Class endpoint."""

MODEL_EXPAND_MAP: dict[str, str | None] = {
    "market_locations": (
        "marketLocations("
        "$expand=calculationRules($expand=usages,formula($expand=formulaSteps),meteringProcedure),"
        "actorsMapping,direction,type"
        ")"
    ),
    "model_operands": "modelOperands",
    "measurement_class": "measurementClass($expand=meteringLocations,actors)",
    "metering_location_purposes": "meteringLocationPurposes($expand=purpose)",
    "concept_type": "conceptType",
    "status": "status",
    "division": "division",
    "all": None,
}
"""``$expand`` map for the Measurement Concept Model endpoint."""


# ---------------------------------------------------------------------------
# Query-parameter builders
# ---------------------------------------------------------------------------


def build_expand(
    include: Sequence[str] | None,
    expand_map: dict[str, str | None] = INSTANCE_EXPAND_MAP,
) -> str | None:
    """Convert a user-friendly *include* list into an OData ``$expand`` value.

    Parameters
    ----------
    include:
        List of expansion names (keys of *expand_map*).  If the list
        contains ``"all"``, the return value is ``"*"`` (expand everything).
        ``None`` or an empty sequence means "no expansion".
    expand_map:
        The endpoint-specific mapping of friendly names to OData fragments.

    Returns
    -------
    str | None
        A comma-separated ``$expand`` string, or ``None`` if nothing to expand.

    Raises
    ------
    ValueError
        If an include name is not found in the expand map.
    """
    if not include:
        return None

    for name in include:
        if name not in expand_map:
            valid = ", ".join(sorted(expand_map))
            raise ValueError(f"Unknown include {name!r}. Valid names: {valid}")

    if "all" in include:
        return "*"

    fragments: list[str] = []
    for name in include:
        value = expand_map[name]
        if value is not None:
            fragments.append(value)
    return ",".join(fragments) if fragments else None


def build_query_params(
    *,
    top: int | None = None,
    skip: int | None = None,
    count: bool = False,
    order_by: str | None = None,
    search: str | None = None,
    expand: str | None = None,
    filters: dict[str, str | None] | None = None,
) -> dict[str, str]:
    """Build an OData V4 query-parameter dictionary.

    All keys use the OData ``$``-prefixed convention.  Filter keys given in
    Python ``snake_case`` are converted to OData wire names via
    :func:`~sap_mcm_client.types_common._to_odata_camel`.

    Parameters
    ----------
    top:
        Maximum number of entities to return (``$top``).
    skip:
        Number of entities to skip (``$skip``).
    count:
        If ``True``, request an inline count (``$count=true``).
    order_by:
        OData ``$orderby`` expression (already in wire format).
    search:
        Free-text search string (``$search``).
    expand:
        Pre-built ``$expand`` string (typically from :func:`build_expand`).
    filters:
        Mapping of Python field names to desired values.  Each entry becomes
        an ``<odata_name> eq '<value>'`` clause; ``None`` values are skipped.
        Clauses are joined with `` and ``.

    Returns
    -------
    dict[str, str]
        Query parameters ready to pass to ``httpx`` as ``params=``.
    """
    params: dict[str, str] = {}

    if top is not None:
        params["$top"] = str(top)
    if skip is not None:
        params["$skip"] = str(skip)
    if count:
        params["$count"] = "true"
    if order_by is not None:
        params["$orderby"] = order_by
    if search is not None:
        params["$search"] = search
    if expand is not None:
        params["$expand"] = expand

    if filters:
        clauses: list[str] = []
        for py_name, value in filters.items():
            if value is None:
                continue
            odata_name = _to_odata_camel(py_name)
            clauses.append(f"{odata_name} eq '{value}'")
        if clauses:
            params["$filter"] = " and ".join(clauses)

    return params


# ---------------------------------------------------------------------------
# Response container
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ListResponse(Generic[T]):
    """Generic container for an OData collection response.

    Attributes
    ----------
    items:
        The parsed entities from the ``value`` array.
    count:
        The total entity count if ``$count=true`` was requested, otherwise
        ``None``.
    """

    items: list[T]
    count: int | None = None


# ---------------------------------------------------------------------------
# Response parsers
# ---------------------------------------------------------------------------

#: Keys injected by OData that are not part of the entity payload.
_ODATA_ENVELOPE_KEYS: frozenset[str] = frozenset(
    {
        "@odata.context",
        "@odata.metadataEtag",
        "@context",
        "@metadataEtag",
    }
)


def parse_entity(data: dict[str, Any], model: type[T]) -> T:
    """Parse a single OData entity response into a Pydantic model.

    Strips OData envelope keys (``@odata.context``, ``@odata.metadataEtag``,
    etc.) before passing the remaining dictionary to the model constructor.

    Parameters
    ----------
    data:
        The raw JSON-decoded response body.
    model:
        The Pydantic model class to deserialize into.

    Returns
    -------
    T
        A validated, frozen model instance.
    """
    cleaned = {k: v for k, v in data.items() if k not in _ODATA_ENVELOPE_KEYS}
    return model.model_validate(cleaned)


def parse_collection(data: dict[str, Any], model: type[T]) -> ListResponse[T]:
    """Parse an OData collection response into a :class:`ListResponse`.

    Expects the standard OData shape::

        {
            "@odata.context": "...",
            "@odata.count": 42,   // optional
            "value": [ ... ]
        }

    Parameters
    ----------
    data:
        The raw JSON-decoded response body.
    model:
        The Pydantic model class for each item in the ``value`` array.

    Returns
    -------
    ListResponse[T]
        The parsed items and optional count.
    """
    raw_items: list[dict[str, Any]] = data.get("value", [])
    items = [model.model_validate(item) for item in raw_items]

    raw_count = data.get("@odata.count")
    count = int(raw_count) if raw_count is not None else None

    return ListResponse(items=items, count=count)
