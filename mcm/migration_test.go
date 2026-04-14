package mcm

import (
	"encoding/json"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ---------------------------------------------------------------------------
// MigrationResponse parsing
// ---------------------------------------------------------------------------

func TestParseMigrationResponse(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_response.json")
	require.NoError(t, err)

	var resp MigrationResponse
	require.NoError(t, json.Unmarshal(data, &resp))

	assert.Equal(t, "f1343cac-b0ee-42aa-af23-43b1f628f61d", resp.RequestID)
}

// ---------------------------------------------------------------------------
// MigrationInstanceResponse parsing
// ---------------------------------------------------------------------------

func TestParseMigrationInstanceResponseTopLevel(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var inst MigrationInstanceResponse
	require.NoError(t, json.Unmarshal(data, &inst))

	assert.Equal(t, "b2c3d4e5-f6a7-8901-bcde-f12345678901", inst.ID)
	assert.Equal(t, "MIG-INST-LEGACY-001", inst.IDText)
	require.NotNil(t, inst.Version)
	assert.Equal(t, "1", *inst.Version)
	require.NotNil(t, inst.Description)
	assert.Equal(t, "Migrated measurement concept instance from legacy system.", *inst.Description)
	require.NotNil(t, inst.DivisionCode)
	assert.Equal(t, "EL", *inst.DivisionCode)
	require.NotNil(t, inst.OverallStatusCode)
	assert.Equal(t, "ACTIVE", *inst.OverallStatusCode)
	require.NotNil(t, inst.Overwrite)
	assert.False(t, *inst.Overwrite)
	require.NotNil(t, inst.ModifiedAt)
	assert.Equal(t, 2024, inst.ModifiedAt.Year())
}

func TestParseMigrationInstanceResponseAddresses(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var inst MigrationInstanceResponse
	require.NoError(t, json.Unmarshal(data, &inst))

	require.Len(t, inst.Addresses, 1)
	addr := inst.Addresses[0]
	assert.Equal(t, "dddddddd-aaaa-bbbb-cccc-111122223333", addr.ID)
	require.NotNil(t, addr.CountryCode)
	assert.Equal(t, "DE", *addr.CountryCode)
	require.NotNil(t, addr.CityName)
	assert.Equal(t, "Walldorf", *addr.CityName)
	require.NotNil(t, addr.Latitude)
	assert.Equal(t, "49.30637000", addr.Latitude.String())
	require.NotNil(t, addr.Longitude)
	assert.Equal(t, "8.64236000", addr.Longitude.String())
}

func TestParseMigrationInstanceResponseMeteringLocations(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var inst MigrationInstanceResponse
	require.NoError(t, json.Unmarshal(data, &inst))

	require.Len(t, inst.MeteringLocations, 1)
	melo := inst.MeteringLocations[0]
	// Migration variant allows up to 60 chars for idText.
	assert.Equal(t, "Migrated Metering Location Z1 (legacy)", melo.IDText)
	// altitude is migration-specific.
	require.NotNil(t, melo.Altitude)
	assert.Equal(t, "125.500", melo.Altitude.String())
	require.NotNil(t, melo.TypeCode)
	assert.Equal(t, "GRIDMES", *melo.TypeCode)
	require.NotNil(t, melo.DeviceSerialID)
	assert.Equal(t, "SER-9876543210", *melo.DeviceSerialID)

	require.Len(t, melo.MeteringTasks, 1)
	task := melo.MeteringTasks[0]
	require.NotNil(t, task.PlannedMeteringProcedureCode)
	assert.Equal(t, "SLP", *task.PlannedMeteringProcedureCode)
	require.NotNil(t, task.PlannedRegisterCode)
	assert.Equal(t, "1.8.x", *task.PlannedRegisterCode)
	require.NotNil(t, task.RegisterCode)
	assert.Equal(t, "1.8.0", *task.RegisterCode)
}

func TestParseMigrationInstanceResponseMarketLocations(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var inst MigrationInstanceResponse
	require.NoError(t, json.Unmarshal(data, &inst))

	require.Len(t, inst.MarketLocations, 1)
	malo := inst.MarketLocations[0]
	assert.Equal(t, "Migrated Market Location VB (legacy)", malo.IDText)
	require.NotNil(t, malo.DirectionCode)
	assert.Equal(t, "OUT", *malo.DirectionCode)
	require.NotNil(t, malo.BillingProcedure)
	assert.Equal(t, "SLP", *malo.BillingProcedure)

	require.Len(t, malo.CalculationRules, 1)
	rule := malo.CalculationRules[0]
	require.NotNil(t, rule.Expression)
	assert.Equal(t, "Z1B", *rule.Expression)
	require.Len(t, rule.Usages, 2)

	require.Len(t, malo.ActorsMapping, 1)
	actorMapping := malo.ActorsMapping[0]
	require.NotNil(t, actorMapping.ActorID)
	assert.Equal(t, "77777777-aaaa-bbbb-cccc-000000000001", *actorMapping.ActorID)
}

func TestParseMigrationInstanceResponseActors(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var inst MigrationInstanceResponse
	require.NoError(t, json.Unmarshal(data, &inst))

	require.Len(t, inst.Actors, 1)
	actor := inst.Actors[0]
	assert.Equal(t, "Migrated Actor VB (residential consumer)", actor.IDText)
	// subType_code and externalActorId are migration-specific.
	require.NotNil(t, actor.SubTypeCode)
	assert.Equal(t, "RESID", *actor.SubTypeCode)
	require.NotNil(t, actor.ExternalActorID)
	assert.Equal(t, "LEGACY-ACT-0815", *actor.ExternalActorID)
	require.NotNil(t, actor.InstallationDate)
	assert.Equal(t, "2024-03-15", *actor.InstallationDate)
	require.NotNil(t, actor.CommercialSetupDate)
	assert.Equal(t, "2024-03-20", *actor.CommercialSetupDate)
	assert.Nil(t, actor.InterruptibleCode)
}

func TestParseMigrationInstanceResponseOperandMappings(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var inst MigrationInstanceResponse
	require.NoError(t, json.Unmarshal(data, &inst))

	require.Len(t, inst.OperandMappings, 1)
	om := inst.OperandMappings[0]
	require.NotNil(t, om.Operand)
	assert.Equal(t, "Z1B", *om.Operand)
	require.NotNil(t, om.MeteringTaskID)
	assert.Equal(t, "33333333-aaaa-bbbb-cccc-000000000001", *om.MeteringTaskID)
}

func TestParseMigrationInstanceResponseStatusAndChangeProcesses(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var inst MigrationInstanceResponse
	require.NoError(t, json.Unmarshal(data, &inst))

	require.NotNil(t, inst.Status)
	require.NotNil(t, inst.Status.InstanceStatusCode)
	assert.Equal(t, "ACTIVE", *inst.Status.InstanceStatusCode)
	require.NotNil(t, inst.Status.ProcessStatusCode)
	assert.Equal(t, "COMPLETED", *inst.Status.ProcessStatusCode)

	require.Len(t, inst.ChangeProcesses, 1)
	cp := inst.ChangeProcesses[0]
	require.NotNil(t, cp.ExternalOrderID)
	assert.Equal(t, "LEGACY-ORD-4711", *cp.ExternalOrderID)
	require.NotNil(t, cp.ExternalProcessID)
	assert.Equal(t, "LEGACY-PROC-0815", *cp.ExternalProcessID)
	require.NotNil(t, cp.ProcessTypeCode)
	assert.Equal(t, "CREATE", *cp.ProcessTypeCode)
	require.NotNil(t, cp.Finished)
	assert.True(t, *cp.Finished)
}

// ---------------------------------------------------------------------------
// Staged list parsing
// ---------------------------------------------------------------------------

func TestParseMigrationStagedListCollection(t *testing.T) {
	data, err := os.ReadFile("../testdata/migration_staged_list.json")
	require.NoError(t, err)

	resp, err := parseODataCollection[StagedMigrationInstance](data)
	require.NoError(t, err)

	require.NotNil(t, resp.Count)
	assert.Equal(t, 3, *resp.Count)
	require.Len(t, resp.Items, 3)

	assert.Equal(t, "STAGED-2026-02-01-01", resp.Items[0].IDText)
	require.NotNil(t, resp.Items[0].StatusCode)
	assert.Equal(t, "MIGRATED", *resp.Items[0].StatusCode)
	require.NotNil(t, resp.Items[0].RequestID)
	assert.Equal(t, "f1343cac-b0ee-42aa-af23-43b1f628f61d", *resp.Items[0].RequestID)
	require.NotNil(t, resp.Items[0].InstanceOverallStatusCode)
	assert.Equal(t, "ACTIVE", *resp.Items[0].InstanceOverallStatusCode)

	// Second entry is FAILED and carries the raw instance payload + reason.
	assert.Equal(t, "STAGED-2026-02-01-02", resp.Items[1].IDText)
	require.NotNil(t, resp.Items[1].StatusCode)
	assert.Equal(t, "FAILED", *resp.Items[1].StatusCode)
	require.NotNil(t, resp.Items[1].StatusReason)
	assert.Contains(t, *resp.Items[1].StatusReason, "Validation error")
	require.NotNil(t, resp.Items[1].Overwrite)
	assert.True(t, *resp.Items[1].Overwrite)
	require.NotNil(t, resp.Items[1].InstanceData)

	// Third entry is RECEIVED — no migration start / end yet.
	assert.Equal(t, "STAGED-2026-02-01-03", resp.Items[2].IDText)
	require.NotNil(t, resp.Items[2].StatusCode)
	assert.Equal(t, "RECEIVED", *resp.Items[2].StatusCode)
	assert.Nil(t, resp.Items[2].TimeMigrationStart)
	assert.Nil(t, resp.Items[2].TimeMigrationEnd)
	assert.Nil(t, resp.Items[2].InstanceOverallStatusCode)
}
