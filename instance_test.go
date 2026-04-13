package mcm

import (
	"encoding/json"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestParseInstanceGet(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	// Top-level fields
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", inst.ID)
	assert.Equal(t, "INST-79", inst.IDText)
	require.NotNil(t, inst.Version)
	assert.Equal(t, "1", *inst.Version)
	require.NotNil(t, inst.Description)
	assert.Equal(t, "Instance Electricity Purchase - Standard - Creation process - Step by Step", *inst.Description)
	require.NotNil(t, inst.MeasurementModelID)
	assert.Equal(t, "ffffffff-2222-2222-2222-100000000001", *inst.MeasurementModelID)
	require.NotNil(t, inst.MeasurementClassID)
	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", *inst.MeasurementClassID)
	require.NotNil(t, inst.LeadingGridCode)
	assert.Equal(t, "SNE956610053427", *inst.LeadingGridCode)
	require.NotNil(t, inst.DivisionCode)
	assert.Equal(t, "EL", *inst.DivisionCode)
	require.NotNil(t, inst.OrdererCode)
	assert.Equal(t, "SP_DIST", *inst.OrdererCode)
	require.NotNil(t, inst.OverallStatusCode)
	assert.Equal(t, "ACTIVE", *inst.OverallStatusCode)
	require.NotNil(t, inst.StatusID)
	assert.Equal(t, "eeeeeeee-4444-5555-6666-777788889999", *inst.StatusID)
	require.NotNil(t, inst.InstalledOn)
	assert.Equal(t, "2024-03-15", *inst.InstalledOn)
	require.NotNil(t, inst.InstalledUntil)
	assert.Equal(t, "9999-12-31", *inst.InstalledUntil)
	require.NotNil(t, inst.CommercialSetupOn)
	assert.Equal(t, "2024-03-20", *inst.CommercialSetupOn)
	assert.Nil(t, inst.PhysicalShutdownOn)
	assert.Nil(t, inst.CommercialShutdownOn)
	require.NotNil(t, inst.DeviceInstallationsReady)
	assert.True(t, *inst.DeviceInstallationsReady)
	require.NotNil(t, inst.MarketLocationsComplete)
	assert.True(t, *inst.MarketLocationsComplete)
	require.NotNil(t, inst.LeadingAddressID)
	assert.Equal(t, "dddddddd-aaaa-bbbb-cccc-111122223333", *inst.LeadingAddressID)
	assert.Nil(t, inst.PredecessorID)
	require.NotNil(t, inst.ModifiedAt)
	assert.Equal(t, 2024, inst.ModifiedAt.Year())
}

func TestParseInstanceGetMeteringLocations(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.MeteringLocations, 1)
	melo := inst.MeteringLocations[0]
	assert.Equal(t, "11111111-aaaa-bbbb-cccc-000000000001", melo.ID)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", melo.MeasurementConceptInstanceID)
	assert.Equal(t, "Z1", melo.IDText)
	require.NotNil(t, melo.TypeCode)
	assert.Equal(t, "GRIDMES", *melo.TypeCode)
	require.NotNil(t, melo.Position)
	assert.Equal(t, 1, *melo.Position)
	require.NotNil(t, melo.MeteringLocationID)
	assert.Equal(t, "DE0001234567890000000000000012345", *melo.MeteringLocationID)
	require.NotNil(t, melo.GridCode)
	assert.Equal(t, "SNE956610053427", *melo.GridCode)
	require.NotNil(t, melo.GridLevelCode)
	assert.Equal(t, "MV", *melo.GridLevelCode)
	require.NotNil(t, melo.Disconnectable)
	assert.False(t, *melo.Disconnectable)
	require.NotNil(t, melo.TransformerRequired)
	assert.False(t, *melo.TransformerRequired)
	require.NotNil(t, melo.DeviceSerialID)
	assert.Equal(t, "SER-9876543210", *melo.DeviceSerialID)
	require.NotNil(t, melo.InstallationDate)
	assert.Equal(t, "2024-03-15", *melo.InstallationDate)
	require.NotNil(t, melo.LocationInstalled)
	assert.True(t, *melo.LocationInstalled)
	require.NotNil(t, melo.LocationRemoved)
	assert.False(t, *melo.LocationRemoved)

	// Decimal loss factor fields
	assert.Equal(t, "0", melo.LossTransformerSupply.String())
	assert.False(t, melo.LossTransformerSupply.IsZero())
	assert.Equal(t, "0", melo.LossLineSupply.String())
	assert.Equal(t, "0", melo.LossTransformerDemand.String())
	assert.Equal(t, "0", melo.LossLineDemand.String())
}

func TestParseInstanceGetMeteringTasks(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.MeteringLocations, 1)
	tasks := inst.MeteringLocations[0].MeteringTasks
	require.Len(t, tasks, 2)

	task1 := tasks[0]
	assert.Equal(t, "33333333-aaaa-bbbb-cccc-000000000001", task1.ID)
	assert.Equal(t, "11111111-aaaa-bbbb-cccc-000000000001", task1.MeteringLocationID)
	require.NotNil(t, task1.DirectionCode)
	assert.Equal(t, "OUT", *task1.DirectionCode)
	require.NotNil(t, task1.TypeCode)
	assert.Equal(t, "AE", *task1.TypeCode)
	require.NotNil(t, task1.Position)
	assert.Equal(t, 1, *task1.Position)
	require.NotNil(t, task1.PlannedMeteringProcedureCode)
	assert.Equal(t, "SLP", *task1.PlannedMeteringProcedureCode)
	require.NotNil(t, task1.PlannedRegisterCode)
	assert.Equal(t, "1.8.x", *task1.PlannedRegisterCode)
	require.NotNil(t, task1.RegisterCode)
	assert.Equal(t, "1.8.0", *task1.RegisterCode)

	// Decimal loss factors on metering task
	assert.Equal(t, "1", task1.LossFactorTransformer.String())
	assert.False(t, task1.LossFactorTransformer.IsZero())
	assert.Equal(t, "1", task1.LossFactorLine.String())
	assert.False(t, task1.LossFactorLine.IsZero())

	task2 := tasks[1]
	assert.Equal(t, "33333333-aaaa-bbbb-cccc-000000000002", task2.ID)
	require.NotNil(t, task2.DirectionCode)
	assert.Equal(t, "IN", *task2.DirectionCode)
	require.NotNil(t, task2.Position)
	assert.Equal(t, 2, *task2.Position)
}

func TestParseInstanceGetMarketLocations(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.MarketLocations, 1)
	malo := inst.MarketLocations[0]
	assert.Equal(t, "44444444-aaaa-bbbb-cccc-000000000001", malo.ID)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", malo.MeasurementConceptInstanceID)
	require.NotNil(t, malo.IDText)
	assert.Equal(t, "Malo VB", *malo.IDText)
	require.NotNil(t, malo.TypeCode)
	assert.Equal(t, "SUPPLY", *malo.TypeCode)
	require.NotNil(t, malo.DirectionCode)
	assert.Equal(t, "OUT", *malo.DirectionCode)
	require.NotNil(t, malo.Position)
	assert.Equal(t, 1, *malo.Position)
	require.NotNil(t, malo.MarketLocationID)
	assert.Equal(t, "51111111111", *malo.MarketLocationID)
	require.NotNil(t, malo.VirtualMarketLocation)
	assert.False(t, *malo.VirtualMarketLocation)
	require.NotNil(t, malo.BillingProcedure)
	assert.Equal(t, "SLP", *malo.BillingProcedure)
	require.NotNil(t, malo.SettlementProcedure)
	assert.Equal(t, "SLP", *malo.SettlementProcedure)
	require.NotNil(t, malo.LocationComplete)
	assert.True(t, *malo.LocationComplete)
}

func TestParseInstanceGetCalculationRules(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.MarketLocations, 1)
	require.Len(t, inst.MarketLocations[0].CalculationRules, 1)
	rule := inst.MarketLocations[0].CalculationRules[0]

	assert.Equal(t, "55555555-aaaa-bbbb-cccc-000000000001", rule.ID)
	assert.Equal(t, "44444444-aaaa-bbbb-cccc-000000000001", rule.MarketLocationID)
	assert.Equal(t, "SLP", rule.MeteringProcedureCode)
	require.NotNil(t, rule.Expression)
	assert.Equal(t, "Z1B", *rule.Expression)
	require.NotNil(t, rule.ExpressionExpanded)
	assert.Equal(t, "Z1B{1,1}", *rule.ExpressionExpanded)

	// Steps
	require.Len(t, rule.Steps, 1)
	step := rule.Steps[0]
	assert.Equal(t, "55555555-aaaa-bbbb-cccc-000000000001", step.CalculationRuleID)
	assert.Equal(t, 0, step.Step)
	require.NotNil(t, step.Type)
	assert.Equal(t, "var", *step.Type)
	require.NotNil(t, step.Value)
	assert.Equal(t, "Z1.OUT", *step.Value)
	require.NotNil(t, step.MeteringTaskID)
	assert.Equal(t, "33333333-aaaa-bbbb-cccc-000000000001", *step.MeteringTaskID)

	// Usages
	require.Len(t, rule.Usages, 3)
	assert.Equal(t, "66666666-aaaa-bbbb-cccc-000000000001", rule.Usages[0].ID)
	require.NotNil(t, rule.Usages[0].UsageCode)
	assert.Equal(t, "GRIDUSE", *rule.Usages[0].UsageCode)
	require.NotNil(t, rule.Usages[1].UsageCode)
	assert.Equal(t, "OUBILL", *rule.Usages[1].UsageCode)
	require.NotNil(t, rule.Usages[2].UsageCode)
	assert.Equal(t, "SETTLE", *rule.Usages[2].UsageCode)
}

func TestParseInstanceGetActors(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.Actors, 1)
	actor := inst.Actors[0]
	assert.Equal(t, "77777777-aaaa-bbbb-cccc-000000000001", actor.ID)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", actor.MeasurementConceptInstanceID)
	assert.Equal(t, "VB", actor.IDText)
	require.NotNil(t, actor.TypeCode)
	assert.Equal(t, "CONSUMER", *actor.TypeCode)
	require.NotNil(t, actor.DirectionCode)
	assert.Equal(t, "OUT", *actor.DirectionCode)
	require.NotNil(t, actor.Position)
	assert.Equal(t, 1, *actor.Position)
	require.NotNil(t, actor.MarketLocationID)
	assert.Equal(t, "44444444-aaaa-bbbb-cccc-000000000001", *actor.MarketLocationID)
	require.NotNil(t, actor.IsOwnConsumption)
	assert.False(t, *actor.IsOwnConsumption)
	assert.Nil(t, actor.PowerRangeCode)
	assert.Nil(t, actor.EnergySourceCode)
	assert.Nil(t, actor.GridLevelCode)
}

func TestParseInstanceGetAddresses(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.Addresses, 1)
	addr := inst.Addresses[0]
	assert.Equal(t, "dddddddd-aaaa-bbbb-cccc-111122223333", addr.ID)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", addr.MeasurementConceptInstanceID)
	require.NotNil(t, addr.CountryCode)
	assert.Equal(t, "DE", *addr.CountryCode)
	require.NotNil(t, addr.CityName)
	assert.Equal(t, "Walldorf", *addr.CityName)
	require.NotNil(t, addr.PostalCode)
	assert.Equal(t, "69190", *addr.PostalCode)
	require.NotNil(t, addr.StreetName)
	assert.Equal(t, "Ringstrasse", *addr.StreetName)
	require.NotNil(t, addr.HouseNumber)
	assert.Equal(t, "981", *addr.HouseNumber)
	require.NotNil(t, addr.FloorNumber)
	assert.Equal(t, "5", *addr.FloorNumber)
	require.NotNil(t, addr.Supplement)
	assert.Equal(t, "5.Stock App 67", *addr.Supplement)
	require.NotNil(t, addr.TimeZone)
	assert.Equal(t, "CEST", *addr.TimeZone)
	assert.Nil(t, addr.CityDistrict)
	assert.Nil(t, addr.HouseNumberSupplement)

	// Latitude and Longitude are decimal pointers
	require.NotNil(t, addr.Latitude)
	assert.Equal(t, "49.30637000", addr.Latitude.String())
	require.NotNil(t, addr.Longitude)
	assert.Equal(t, "8.64236000", addr.Longitude.String())
}

func TestParseInstanceGetChangeProcesses(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.ChangeProcesses, 1)
	cp := inst.ChangeProcesses[0]
	assert.Equal(t, "aaaaaaaa-bbbb-cccc-dddd-000000000001", cp.ID)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", cp.MeasurementConceptInstanceID)
	require.NotNil(t, cp.ExternalOrderID)
	assert.Equal(t, "4711", *cp.ExternalOrderID)
	require.NotNil(t, cp.ProcessTypeCode)
	assert.Equal(t, "CREATE", *cp.ProcessTypeCode)
	require.NotNil(t, cp.Finished)
	assert.True(t, *cp.Finished)
	require.NotNil(t, cp.ModifiedAt)

	// Process data
	require.NotNil(t, cp.ProcessData)
	pd := cp.ProcessData
	assert.Equal(t, "bbbbbbbb-cccc-dddd-eeee-000000000001", pd.ID)
	assert.Equal(t, "aaaaaaaa-bbbb-cccc-dddd-000000000001", pd.ChangeProcessID)
	require.NotNil(t, pd.LeadingConnectionUser)
	assert.Equal(t, "0815", *pd.LeadingConnectionUser)
	require.NotNil(t, pd.LeadingConnectionOwner)
	assert.Equal(t, "0815", *pd.LeadingConnectionOwner)
	require.NotNil(t, pd.Note)
	assert.Contains(t, *pd.Note, "Standard electricity purchase")
	require.NotNil(t, pd.InitialDataEntryReady)
	assert.True(t, *pd.InitialDataEntryReady)
	require.NotNil(t, pd.DeviceInstallationsReady)
	assert.True(t, *pd.DeviceInstallationsReady)
	require.NotNil(t, pd.MarketLocationsComplete)
	assert.True(t, *pd.MarketLocationsComplete)

	// Metering locations PD
	require.Len(t, pd.MeteringLocationsPD, 1)
	meloPD := pd.MeteringLocationsPD[0]
	assert.Equal(t, "cccccccc-dddd-eeee-ffff-000000000001", meloPD.ID)
	require.NotNil(t, meloPD.LocationIdentifierReady)
	assert.True(t, *meloPD.LocationIdentifierReady)
	require.NotNil(t, meloPD.MasterDataReady)
	assert.True(t, *meloPD.MasterDataReady)

	// Market locations PD
	require.Len(t, pd.MarketLocationsPD, 1)
	maloPD := pd.MarketLocationsPD[0]
	assert.Equal(t, "cccccccc-dddd-eeee-ffff-000000000002", maloPD.ID)

	// Actors PD
	require.Len(t, pd.ActorsPD, 1)
	actorPD := pd.ActorsPD[0]
	assert.Equal(t, "cccccccc-dddd-eeee-ffff-000000000003", actorPD.ID)
	assert.Equal(t, "77777777-aaaa-bbbb-cccc-000000000001", actorPD.ActorID)

	// Instance characteristics
	require.Len(t, cp.InstanceCharacteristics, 2)
	ic1 := cp.InstanceCharacteristics[0]
	assert.Equal(t, "dddddddd-eeee-ffff-0000-000000000001", ic1.ID)
	require.NotNil(t, ic1.EntityTypeCode)
	assert.Equal(t, "MCIMeteringTask", *ic1.EntityTypeCode)
	require.NotNil(t, ic1.CharacteristicCode)
	assert.Equal(t, "selectPlannedMeteringProcedure", *ic1.CharacteristicCode)
	require.NotNil(t, ic1.Value)
	assert.Equal(t, "SLP", *ic1.Value)
}

func TestParseInstanceGetStatus(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.Statuses, 1)
	status := inst.Statuses[0]
	assert.Equal(t, "eeeeeeee-4444-5555-6666-777788889999", status.ID)
	assert.Equal(t, "aaaaaaaa-bbbb-cccc-dddd-000000000001", status.ChangeProcessID)
	require.NotNil(t, status.InstanceStatusCode)
	assert.Equal(t, "ACTIVE", *status.InstanceStatusCode)
	require.NotNil(t, status.ProcessStatusCode)
	assert.Equal(t, "COMPLETED", *status.ProcessStatusCode)
}

func TestParseInstanceGetOperandMappings(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_get.json")
	require.NoError(t, err)

	var inst MeasurementConceptInstance
	err = json.Unmarshal(data, &inst)
	require.NoError(t, err)

	require.Len(t, inst.OperandMappings, 1)
	om := inst.OperandMappings[0]
	assert.Equal(t, "99999999-aaaa-bbbb-cccc-000000000001", om.ID)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", om.MeasurementConceptInstanceID)
	require.NotNil(t, om.Operand)
	assert.Equal(t, "Z1B", *om.Operand)
	require.NotNil(t, om.MeteringTaskID)
	assert.Equal(t, "33333333-aaaa-bbbb-cccc-000000000001", *om.MeteringTaskID)
	require.NotNil(t, om.Position)
	assert.Equal(t, 1, *om.Position)
}

func TestParseInstanceListCollection(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_list.json")
	require.NoError(t, err)

	resp, err := parseODataCollection[MeasurementConceptInstance](data)
	require.NoError(t, err)

	require.NotNil(t, resp.Count)
	assert.Equal(t, 2, *resp.Count)
	require.Len(t, resp.Items, 2)

	// First item
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", resp.Items[0].ID)
	assert.Equal(t, "INST-79", resp.Items[0].IDText)
	require.NotNil(t, resp.Items[0].DivisionCode)
	assert.Equal(t, "EL", *resp.Items[0].DivisionCode)
	require.NotNil(t, resp.Items[0].OverallStatusCode)
	assert.Equal(t, "ACTIVE", *resp.Items[0].OverallStatusCode)

	// Second item
	assert.Equal(t, "b2c3d4e5-f6a7-8901-bcde-f12345678901", resp.Items[1].ID)
	assert.Equal(t, "INST-80", resp.Items[1].IDText)
	require.NotNil(t, resp.Items[1].DivisionCode)
	assert.Equal(t, "GA", *resp.Items[1].DivisionCode)
	require.NotNil(t, resp.Items[1].OverallStatusCode)
	assert.Equal(t, "NEW", *resp.Items[1].OverallStatusCode)
}
