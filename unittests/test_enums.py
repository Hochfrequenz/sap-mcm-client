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
    MeteringLocationType,
    MeteringLocationPurpose,
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
        assert Division.ELECTRICITY == "EL"
        assert Division.GAS == "GA"
        assert Division.WATER == "WA"
        assert Division.REMOTE_HEAT == "RH"

    def test_str_comparison(self) -> None:
        """StrEnum members compare equal to plain strings."""
        assert Division.ELECTRICITY == "EL"
        assert "EL" == Division.ELECTRICITY

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
        assert OverallStatus.INITIAL == "INITIAL"
        assert OverallStatus.NEW == "NEW"
        assert OverallStatus.ERROR == "ERROR"
        assert OverallStatus.ACTIVE == "ACTIVE"
        assert OverallStatus.HISTORIC == "HISTORIC"
        assert OverallStatus.VERSION_CANCEL == "VERSION_CANCEL"

    def test_member_count(self) -> None:
        assert len(OverallStatus) == 6


class TestClassType:
    """Tests for the ClassType enum."""

    def test_members_exist(self) -> None:
        assert ClassType.CLASS == "CLASS"
        assert ClassType.SAP_TEMPLATE == "SAPTEMPLATE"

    def test_member_count(self) -> None:
        assert len(ClassType) == 2


class TestConceptType:
    """Tests for the ConceptType enum."""

    def test_members_exist(self) -> None:
        assert ConceptType.MODEL == "MODEL"
        assert ConceptType.SAP_TEMPLATE == "SAPTEMPLATE"


class TestModelStatus:
    """Tests for the ModelStatus enum."""

    def test_members_exist(self) -> None:
        assert ModelStatus.IN_PROGRESS == "IN_PROGRESS"
        assert ModelStatus.ACTIVE == "ACTIVE"
        assert ModelStatus.DEACTIVATED == "DEACTIVATED"


class TestDirection:
    """Tests for the Direction enum."""

    def test_members_exist(self) -> None:
        assert Direction.IN == "IN"
        assert Direction.OUT == "OUT"


class TestActorType:
    """Tests for the ActorType enum."""

    def test_members_exist(self) -> None:
        assert ActorType.CONSUMER == "CONSUMER"
        assert ActorType.PRODUCER == "PRODUCER"
        assert ActorType.STORAGE == "STORAGE"


class TestMeteringLocationType:
    """Tests for the MeteringLocationType enum."""

    def test_members_exist(self) -> None:
        assert MeteringLocationType.GRID_MES == "GRIDMES"
        assert MeteringLocationType.SERIES_MES == "SERIESMES"
        assert MeteringLocationType.GENERATOR_MES == "GENERATORMES"
        assert MeteringLocationType.STORAGE_MES == "STORAGEMES"
        assert MeteringLocationType.DIFF_MES == "DIFFMES"
        assert MeteringLocationType.COMPARE_MES == "COMPAREMES"

    def test_member_count(self) -> None:
        assert len(MeteringLocationType) == 6


class TestMeteringTaskType:
    """Tests for the MeteringTaskType enum."""

    def test_members_exist(self) -> None:
        assert MeteringTaskType.AE == "AE"
        assert MeteringTaskType.OV == "OV"
        assert MeteringTaskType.EV == "EV"


class TestMeteringProcedure:
    """Tests for the MeteringProcedure enum."""

    def test_members_exist(self) -> None:
        assert MeteringProcedure.SLP == "SLP"
        assert MeteringProcedure.RLM == "RLM"
        assert MeteringProcedure.IR == "IR"


class TestMarketLocationUsage:
    """Tests for the MarketLocationUsage enum."""

    def test_members_exist(self) -> None:
        assert MarketLocationUsage.BILLING == "BILLING"
        assert MarketLocationUsage.GRID_USE == "GRIDUSE"
        assert MarketLocationUsage.OU_BILL == "OUBILL"
        assert MarketLocationUsage.REB == "REB"
        assert MarketLocationUsage.SETTLE == "SETTLE"

    def test_member_count(self) -> None:
        assert len(MarketLocationUsage) == 5


class TestMarketLocationType:
    """Tests for the MarketLocationType enum."""

    def test_members_exist(self) -> None:
        assert MarketLocationType.SUPPLY == "SUPPLY"


class TestProcessType:
    """Tests for the ProcessType enum."""

    def test_members_exist(self) -> None:
        assert ProcessType.CREATE == "CREATE"


class TestMeteringLocationPurpose:
    """Tests for the MeteringLocationPurpose enum."""

    def test_members_exist(self) -> None:
        assert MeteringLocationPurpose.SC == "SC"
        assert MeteringLocationPurpose.CST == "CST"


class TestForecastBasis:
    """Tests for the ForecastBasis enum."""

    def test_members_exist(self) -> None:
        assert ForecastBasis.RLM == "RLM"
        assert ForecastBasis.REM == "REM"
        assert ForecastBasis.HO == "HO"


class TestMeasuringType:
    """Tests for the MeasuringType enum."""

    def test_members_exist(self) -> None:
        assert MeasuringType.CME == "CME"
        assert MeasuringType.MME == "MME"


class TestRate:
    """Tests for the Rate enum."""

    def test_members_exist(self) -> None:
        assert Rate.SINGLE_RATE == "SR"
        assert Rate.DOUBLE_RATE == "DR"


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
    assert Division.ELECTRICITY != "UNKNOWN_DIVISION"
    assert "SOME_OTHER" != OverallStatus.ACTIVE
