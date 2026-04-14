package mcm

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDivisionConstants(t *testing.T) {
	assert.Equal(t, Division("EL"), DivisionElectricity)
	assert.Equal(t, Division("GA"), DivisionGas)
	assert.Equal(t, Division("WA"), DivisionWater)
	assert.Equal(t, Division("RH"), DivisionRemoteHeat)
}

func TestOverallStatusConstants(t *testing.T) {
	assert.Equal(t, OverallStatus("INITIAL"), OverallStatusInitial)
	assert.Equal(t, OverallStatus("NEW"), OverallStatusNew)
	assert.Equal(t, OverallStatus("ERROR"), OverallStatusError)
	assert.Equal(t, OverallStatus("ACTIVE"), OverallStatusActive)
	assert.Equal(t, OverallStatus("HISTORIC"), OverallStatusHistoric)
	assert.Equal(t, OverallStatus("VERSION_CANCEL"), OverallStatusVersionCancel)
}

func TestClassTypeConstants(t *testing.T) {
	assert.Equal(t, ClassType("CLASS"), ClassTypeClass)
	assert.Equal(t, ClassType("SAPTEMPLATE"), ClassTypeSAPTemplate)
}

func TestConceptTypeConstants(t *testing.T) {
	assert.Equal(t, ConceptType("MODEL"), ConceptTypeModel)
	assert.Equal(t, ConceptType("SAPTEMPLATE"), ConceptTypeSAPTemplate)
}

func TestModelStatusConstants(t *testing.T) {
	assert.Equal(t, ModelStatus("IN_PROGRESS"), ModelStatusInProgress)
	assert.Equal(t, ModelStatus("ACTIVE"), ModelStatusActive)
	assert.Equal(t, ModelStatus("DEACTIVATED"), ModelStatusDeactivated)
}

func TestDirectionConstants(t *testing.T) {
	assert.Equal(t, Direction("IN"), DirectionIn)
	assert.Equal(t, Direction("OUT"), DirectionOut)
}

func TestActorTypeConstants(t *testing.T) {
	assert.Equal(t, ActorType("CONSUMER"), ActorTypeConsumer)
	assert.Equal(t, ActorType("PRODUCER"), ActorTypeProducer)
	assert.Equal(t, ActorType("STORAGE"), ActorTypeStorage)
}

func TestMeteringLocationTypeConstants(t *testing.T) {
	assert.Equal(t, MeteringLocationType("GRIDMES"), MeteringLocationTypeGridMes)
	assert.Equal(t, MeteringLocationType("SERIESMES"), MeteringLocationTypeSeriesMes)
	assert.Equal(t, MeteringLocationType("GENERATORMES"), MeteringLocationTypeGeneratorMes)
	assert.Equal(t, MeteringLocationType("STORAGEMES"), MeteringLocationTypeStorageMes)
	assert.Equal(t, MeteringLocationType("DIFFMES"), MeteringLocationTypeDiffMes)
	assert.Equal(t, MeteringLocationType("COMPAREMES"), MeteringLocationTypeCompareMes)
}

func TestMeteringTaskTypeConstants(t *testing.T) {
	assert.Equal(t, MeteringTaskType("AE"), MeteringTaskTypeAE)
	assert.Equal(t, MeteringTaskType("OV"), MeteringTaskTypeOV)
	assert.Equal(t, MeteringTaskType("EV"), MeteringTaskTypeEV)
}

func TestMeteringProcedureConstants(t *testing.T) {
	assert.Equal(t, MeteringProcedure("SLP"), MeteringProcedureSLP)
	assert.Equal(t, MeteringProcedure("RLM"), MeteringProcedureRLM)
	assert.Equal(t, MeteringProcedure("IR"), MeteringProcedureIR)
}

func TestMarketLocationUsageConstants(t *testing.T) {
	assert.Equal(t, MarketLocationUsage("BILLING"), MarketLocationUsageBilling)
	assert.Equal(t, MarketLocationUsage("GRIDUSE"), MarketLocationUsageGridUse)
	assert.Equal(t, MarketLocationUsage("OUBILL"), MarketLocationUsageOUBill)
	assert.Equal(t, MarketLocationUsage("REB"), MarketLocationUsageREB)
	assert.Equal(t, MarketLocationUsage("SETTLE"), MarketLocationUsageSettle)
}

func TestMarketLocationTypeConstants(t *testing.T) {
	assert.Equal(t, MarketLocationType("SUPPLY"), MarketLocationTypeSupply)
}

func TestProcessTypeConstants(t *testing.T) {
	assert.Equal(t, ProcessType("CREATE"), ProcessTypeCreate)
}

func TestMeteringLocationPurposeConstants(t *testing.T) {
	assert.Equal(t, MeteringLocationPurpose("SC"), MeteringLocationPurposeSC)
	assert.Equal(t, MeteringLocationPurpose("CST"), MeteringLocationPurposeCST)
}

func TestForecastBasisConstants(t *testing.T) {
	assert.Equal(t, ForecastBasis("RLM"), ForecastBasisRLM)
	assert.Equal(t, ForecastBasis("REM"), ForecastBasisREM)
	assert.Equal(t, ForecastBasis("HO"), ForecastBasisHO)
}

func TestMeasuringTypeConstants(t *testing.T) {
	assert.Equal(t, MeasuringType("CME"), MeasuringTypeCME)
	assert.Equal(t, MeasuringType("MME"), MeasuringTypeMME)
}

func TestRateConstants(t *testing.T) {
	assert.Equal(t, Rate("SR"), RateSingleRate)
	assert.Equal(t, Rate("DR"), RateDoubleRate)
}

func TestEnumStringConversion(t *testing.T) {
	// Enums are typed strings, so string conversion should work naturally.
	assert.Equal(t, "EL", string(DivisionElectricity))
	assert.Equal(t, "ACTIVE", string(OverallStatusActive))
	assert.Equal(t, "OUT", string(DirectionOut))
	assert.Equal(t, "CONSUMER", string(ActorTypeConsumer))
}

func TestEnumFromUnknownValue(t *testing.T) {
	// Unknown values should still deserialize correctly as typed strings.
	d := Division("XX")
	assert.Equal(t, "XX", string(d))
}
