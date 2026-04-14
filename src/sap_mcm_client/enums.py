"""StrEnum types for all SAP MCM domain codes.

These enum values are derived from the OpenAPI specs (v1.1.0) downloaded from
api.sap.com on 2026-04-13. The real SAP system may accept additional codes
not listed here. All enums use StrEnum so that unknown values from the API
can still be compared as plain strings without breaking deserialization —
Pydantic will accept any string, not just the known members, when the field
type is ``str | SomeEnum`` or when ``extra="ignore"`` is set.
"""

from enum import StrEnum


class Division(StrEnum):
    """The energy division of a measurement concept.

    The supported divisions are electricity, gas, water, and remote heat.
    The division is derived from the referenced measurement concept model and class.
    """

    ELECTRICITY = "EL"
    """Electricity"""
    GAS = "GA"
    """Gas"""
    WATER = "WA"
    """Water"""
    REMOTE_HEAT = "RH"
    """Remote heat"""


class OverallStatus(StrEnum):
    """The combined status of the instance status and the process status of a measurement concept instance."""

    INITIAL = "INITIAL"
    """The instance has been created but not yet processed."""
    NEW = "NEW"
    """The instance is new and awaiting processing."""
    ERROR = "ERROR"
    """An error occurred during processing."""
    ACTIVE = "ACTIVE"
    """The instance is active and operational."""
    HISTORIC = "HISTORIC"
    """The instance has been superseded by a newer version."""
    VERSION_CANCEL = "VERSION_CANCEL"
    """The instance version has been cancelled."""


class ClassType(StrEnum):
    """The type of a measurement concept class.

    SAP templates are read-only reference templates; CLASS is production-usable.
    """

    CLASS = "CLASS"
    """A production-usable measurement concept class."""
    SAP_TEMPLATE = "SAPTEMPLATE"
    """A read-only SAP reference template."""


class ConceptType(StrEnum):
    """The type of a measurement concept model.

    SAP templates are read-only reference templates; MODEL is production-usable.
    """

    MODEL = "MODEL"
    """A production-usable measurement concept model."""
    SAP_TEMPLATE = "SAPTEMPLATE"
    """A read-only SAP reference template."""


class ModelStatus(StrEnum):
    """The status of a measurement concept model."""

    IN_PROGRESS = "IN_PROGRESS"
    """The model is being edited."""
    ACTIVE = "ACTIVE"
    """The model is active and can be used for instantiation."""
    DEACTIVATED = "DEACTIVATED"
    """The model has been deactivated."""


class Direction(StrEnum):
    """The energy flow direction of an actor or market location.

    For the electricity division, both IN (supply/feed-in) and OUT (demand/consumption)
    are supported. For gas, water, and remote heat, only OUT is supported.
    """

    IN = "IN"
    """Supply / feed-in direction."""
    OUT = "OUT"
    """Demand / consumption direction."""


class ActorType(StrEnum):
    """The type of an actor in a measurement concept."""

    CONSUMER = "CONSUMER"
    """A consumer of energy."""
    PRODUCER = "PRODUCER"
    """A producer / generator of energy."""
    STORAGE = "STORAGE"
    """An energy storage unit."""


class MeteringLocationType(StrEnum):
    """The type of a metering location within a measurement concept class.

    Defines the role of the metering location in the circuit plan.
    """

    GRID_MES = "GRIDMES"
    """Grid measurement point."""
    SERIES_MES = "SERIESMES"
    """Serial switching measurement point."""
    GENERATOR_MES = "GENERATORMES"
    """Generator measurement point."""
    STORAGE_MES = "STORAGEMES"
    """Storage measurement point."""
    DIFF_MES = "DIFFMES"
    """Difference measurement point."""
    COMPARE_MES = "COMPAREMES"
    """Comparative measurement point."""


class MeteringTaskType(StrEnum):
    """The type of a metering task assigned to a metering location."""

    AE = "AE"
    """Active energy measurement (Arbeitsenergieerfassung)."""
    OV = "OV"
    """Operating volume measurement (Betriebsvolumen)."""
    EV = "EV"
    """Energetic value measurement (Energetischer Wert)."""


class MeteringProcedure(StrEnum):
    """The metering procedure of a metering task or calculation rule.

    Determines how meter readings are collected and processed.
    """

    SLP = "SLP"
    """Standard load profile (Standardlastprofil)."""
    RLM = "RLM"
    """Interval reading / registrierende Leistungsmessung."""
    IR = "IR"
    """Interval recording."""


class MarketLocationUsage(StrEnum):
    """The usage purpose of a market location calculation rule."""

    BILLING = "BILLING"
    """Used for billing."""
    GRID_USE = "GRIDUSE"
    """Used for grid usage calculation."""
    OU_BILL = "OUBILL"
    """Used for own-use billing."""
    REB = "REB"
    """Used for rebilling."""
    SETTLE = "SETTLE"
    """Used for settlement."""


class MarketLocationType(StrEnum):
    """The type of a market location."""

    SUPPLY = "SUPPLY"
    """A supply market location."""


class ProcessType(StrEnum):
    """The type of a change process for a measurement concept instance."""

    CREATE = "CREATE"
    """Initial creation of the instance."""


class MeteringLocationPurpose(StrEnum):
    """The purpose of a metering location in a measurement concept model."""

    SC = "SC"
    """Self-consumption (Eigenverbrauch)."""
    CST = "CST"
    """Commercial settlement transfer."""


class ForecastBasis(StrEnum):
    """The forecast basis of a market location."""

    RLM = "RLM"
    """Interval reading based forecast."""
    REM = "REM"
    """Remainder based forecast."""
    HO = "HO"
    """Household based forecast."""


class MeasuringType(StrEnum):
    """The measuring type of a metering location in process data."""

    CME = "CME"
    """Conventional metering equipment."""
    MME = "MME"
    """Modern metering equipment (smart meter)."""


class Rate(StrEnum):
    """The tariff rate code of a metering task."""

    SINGLE_RATE = "SR"
    """Single rate tariff (Eintarif)."""
    DOUBLE_RATE = "DR"
    """Double rate tariff (Doppeltarif)."""
