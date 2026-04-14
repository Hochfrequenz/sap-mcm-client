"""Tests for the SAP MCM enum types."""

from __future__ import annotations

import pytest

from sap_mcm_client import (
    ActorType,
    ClassType,
    ConceptType,
    Direction,
    Division,
    ForecastBasis,
    MarketLocationType,
    MarketLocationUsage,
    MeasuringType,
    MeteringLocationPurpose,
    MeteringLocationType,
    MeteringProcedure,
    MeteringTaskType,
    ModelStatus,
    OverallStatus,
    ProcessType,
    Rate,
)


class TestDivision:
    """Tests for the Division enum."""

    def test_members_exist(self) -> None:
        assert Division.ELECTRICITY.value == "EL"
        assert Division.GAS.value == "GA"
        assert Division.WATER.value == "WA"
        assert Division.REMOTE_HEAT.value == "RH"

    def test_str_comparison(self) -> None:
        """StrEnum members compare equal to plain strings."""
        # Cast through str() so mypy doesn't narrow to the enum Literal.
        assert str(Division.ELECTRICITY) == "EL"
        assert "EL" == str(Division.ELECTRICITY)

    def test_construction_from_value(self) -> None:
        assert Division("EL") is Division.ELECTRICITY
        assert Division("GA") is Division.GAS

    def test_str_cast(self) -> None:
        assert str(Division.ELECTRICITY) == "EL"

    def test_member_count(self) -> None:
        assert len(Division) == 4


class TestOverallStatus:
    """Tests for the OverallStatus enum."""

    def test_members_exist(self) -> None:
        assert OverallStatus.INITIAL.value == "INITIAL"
        assert OverallStatus.NEW.value == "NEW"
        assert OverallStatus.ERROR.value == "ERROR"
        assert OverallStatus.ACTIVE.value == "ACTIVE"
        assert OverallStatus.HISTORIC.value == "HISTORIC"
        assert OverallStatus.VERSION_CANCEL.value == "VERSION_CANCEL"

    def test_member_count(self) -> None:
        assert len(OverallStatus) == 6


class TestClassType:
    """Tests for the ClassType enum."""

    def test_members_exist(self) -> None:
        assert ClassType.CLASS.value == "CLASS"
        assert ClassType.SAP_TEMPLATE.value == "SAPTEMPLATE"

    def test_member_count(self) -> None:
        assert len(ClassType) == 2


class TestConceptType:
    """Tests for the ConceptType enum."""

    def test_members_exist(self) -> None:
        assert ConceptType.MODEL.value == "MODEL"
        assert ConceptType.SAP_TEMPLATE.value == "SAPTEMPLATE"


class TestModelStatus:
    """Tests for the ModelStatus enum."""

    def test_members_exist(self) -> None:
        assert ModelStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert ModelStatus.ACTIVE.value == "ACTIVE"
        assert ModelStatus.DEACTIVATED.value == "DEACTIVATED"


class TestDirection:
    """Tests for the Direction enum."""

    def test_members_exist(self) -> None:
        assert Direction.IN.value == "IN"
        assert Direction.OUT.value == "OUT"


class TestActorType:
    """Tests for the ActorType enum."""

    def test_members_exist(self) -> None:
        assert ActorType.CONSUMER.value == "CONSUMER"
        assert ActorType.PRODUCER.value == "PRODUCER"
        assert ActorType.STORAGE.value == "STORAGE"


class TestMeteringLocationType:
    """Tests for the MeteringLocationType enum."""

    def test_members_exist(self) -> None:
        assert MeteringLocationType.GRID_MES.value == "GRIDMES"
        assert MeteringLocationType.SERIES_MES.value == "SERIESMES"
        assert MeteringLocationType.GENERATOR_MES.value == "GENERATORMES"
        assert MeteringLocationType.STORAGE_MES.value == "STORAGEMES"
        assert MeteringLocationType.DIFF_MES.value == "DIFFMES"
        assert MeteringLocationType.COMPARE_MES.value == "COMPAREMES"

    def test_member_count(self) -> None:
        assert len(MeteringLocationType) == 6


class TestMeteringTaskType:
    """Tests for the MeteringTaskType enum."""

    def test_members_exist(self) -> None:
        assert MeteringTaskType.AE.value == "AE"
        assert MeteringTaskType.OV.value == "OV"
        assert MeteringTaskType.EV.value == "EV"


class TestMeteringProcedure:
    """Tests for the MeteringProcedure enum."""

    def test_members_exist(self) -> None:
        assert MeteringProcedure.SLP.value == "SLP"
        assert MeteringProcedure.RLM.value == "RLM"
        assert MeteringProcedure.IR.value == "IR"


class TestMarketLocationUsage:
    """Tests for the MarketLocationUsage enum."""

    def test_members_exist(self) -> None:
        assert MarketLocationUsage.BILLING.value == "BILLING"
        assert MarketLocationUsage.GRID_USE.value == "GRIDUSE"
        assert MarketLocationUsage.OU_BILL.value == "OUBILL"
        assert MarketLocationUsage.REB.value == "REB"
        assert MarketLocationUsage.SETTLE.value == "SETTLE"

    def test_member_count(self) -> None:
        assert len(MarketLocationUsage) == 5


class TestMarketLocationType:
    """Tests for the MarketLocationType enum."""

    def test_members_exist(self) -> None:
        assert MarketLocationType.SUPPLY.value == "SUPPLY"


class TestProcessType:
    """Tests for the ProcessType enum."""

    def test_members_exist(self) -> None:
        assert ProcessType.CREATE.value == "CREATE"


class TestMeteringLocationPurpose:
    """Tests for the MeteringLocationPurpose enum."""

    def test_members_exist(self) -> None:
        assert MeteringLocationPurpose.SC.value == "SC"
        assert MeteringLocationPurpose.CST.value == "CST"


class TestForecastBasis:
    """Tests for the ForecastBasis enum."""

    def test_members_exist(self) -> None:
        assert ForecastBasis.RLM.value == "RLM"
        assert ForecastBasis.REM.value == "REM"
        assert ForecastBasis.HO.value == "HO"


class TestMeasuringType:
    """Tests for the MeasuringType enum."""

    def test_members_exist(self) -> None:
        assert MeasuringType.CME.value == "CME"
        assert MeasuringType.MME.value == "MME"


class TestRate:
    """Tests for the Rate enum."""

    def test_members_exist(self) -> None:
        assert Rate.SINGLE_RATE.value == "SR"
        assert Rate.DOUBLE_RATE.value == "DR"


@pytest.mark.parametrize(
    ("enum_class", "value"),
    [
        (Division, "EL"),
        (OverallStatus, "ACTIVE"),
        (ClassType, "CLASS"),
        (Direction, "OUT"),
        (MeteringProcedure, "SLP"),
    ],
)
def test_strenum_is_str_subclass(enum_class: type, value: str) -> None:
    """All enums are StrEnum and thus also str instances."""
    member = enum_class(value)
    assert isinstance(member, str)


def test_unknown_value_comparison_does_not_crash() -> None:
    """Comparing a StrEnum member to an unknown string value should not raise."""
    # Use str() cast so mypy considers the comparison valid.
    assert str(Division.ELECTRICITY) != "UNKNOWN_DIVISION"
    assert "SOME_OTHER" != str(OverallStatus.ACTIVE)
