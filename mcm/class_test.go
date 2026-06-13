package mcm

import (
	"encoding/json"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestParseClassGet(t *testing.T) {
	data, err := os.ReadFile("../testdata/class_get.json")
	require.NoError(t, err)

	var cls MeasurementConceptClass
	err = json.Unmarshal(data, &cls)
	require.NoError(t, err)

	// Top-level fields
	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", cls.ID)
	require.NotNil(t, cls.IDText)
	assert.Equal(t, "P_S", *cls.IDText)
	require.NotNil(t, cls.Name)
	assert.Equal(t, "Feed-in with unmetered generating plant", *cls.Name)
	require.NotNil(t, cls.Description)
	assert.Equal(t, "For mapping models for feed-in with unmetered generation plant", *cls.Description)
	require.NotNil(t, cls.ClassTypeCode)
	assert.Equal(t, "CLASS", *cls.ClassTypeCode)
	require.NotNil(t, cls.Version)
	assert.Equal(t, "1", *cls.Version)
	require.NotNil(t, cls.DivisionCode)
	assert.Equal(t, "EL", *cls.DivisionCode)

	// Expanded ClassType
	require.NotNil(t, cls.ClassType)
	assert.Equal(t, "CLASS", cls.ClassType.Code)
	require.NotNil(t, cls.ClassType.Name)
	assert.Equal(t, "Class", *cls.ClassType.Name)
	require.NotNil(t, cls.ClassType.Descr)
	assert.Equal(t, "Measurement Concept Class", *cls.ClassType.Descr)

	// Expanded Division
	require.NotNil(t, cls.Division)
	assert.Equal(t, "EL", cls.Division.Code)
	require.NotNil(t, cls.Division.Name)
	assert.Equal(t, "Electricity", *cls.Division.Name)
}

func TestParseClassGetMeteringLocations(t *testing.T) {
	data, err := os.ReadFile("../testdata/class_get.json")
	require.NoError(t, err)

	var cls MeasurementConceptClass
	err = json.Unmarshal(data, &cls)
	require.NoError(t, err)

	require.Len(t, cls.MeteringLocations, 2)

	ml1 := cls.MeteringLocations[0]
	assert.Equal(t, "22222222-aaaa-bbbb-cccc-000000000001", ml1.ID)
	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", ml1.MeasurementConceptClassID)
	require.NotNil(t, ml1.IDText)
	assert.Equal(t, "Z1", *ml1.IDText)
	require.NotNil(t, ml1.TypeCode)
	assert.Equal(t, "GRIDMES", *ml1.TypeCode)
	require.NotNil(t, ml1.Description)
	assert.Equal(t, "Grid measurement point", *ml1.Description)
	require.NotNil(t, ml1.Optional)
	assert.False(t, *ml1.Optional)
	require.NotNil(t, ml1.Repeatable)
	assert.False(t, *ml1.Repeatable)
	require.NotNil(t, ml1.Position)
	assert.Equal(t, 1, *ml1.Position)

	ml2 := cls.MeteringLocations[1]
	assert.Equal(t, "22222222-aaaa-bbbb-cccc-000000000002", ml2.ID)
	require.NotNil(t, ml2.TypeCode)
	assert.Equal(t, "GENERATORMES", *ml2.TypeCode)
	require.NotNil(t, ml2.Optional)
	assert.True(t, *ml2.Optional)
}

func TestParseClassGetActors(t *testing.T) {
	data, err := os.ReadFile("../testdata/class_get.json")
	require.NoError(t, err)

	var cls MeasurementConceptClass
	err = json.Unmarshal(data, &cls)
	require.NoError(t, err)

	require.Len(t, cls.Actors, 2)

	a1 := cls.Actors[0]
	assert.Equal(t, "88888888-aaaa-bbbb-cccc-000000000001", a1.ID)
	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", a1.MeasurementConceptClassID)
	require.NotNil(t, a1.IDText)
	assert.Equal(t, "VB1", *a1.IDText)
	require.NotNil(t, a1.TypeCode)
	assert.Equal(t, "CONSUMER", *a1.TypeCode)
	require.NotNil(t, a1.DirectionCode)
	assert.Equal(t, "OUT", *a1.DirectionCode)
	require.NotNil(t, a1.Optional)
	assert.False(t, *a1.Optional)
	assert.Nil(t, a1.EnergySourceCode)

	a2 := cls.Actors[1]
	assert.Equal(t, "88888888-aaaa-bbbb-cccc-000000000002", a2.ID)
	require.NotNil(t, a2.TypeCode)
	assert.Equal(t, "PRODUCER", *a2.TypeCode)
	require.NotNil(t, a2.DirectionCode)
	assert.Equal(t, "IN", *a2.DirectionCode)
	require.NotNil(t, a2.Optional)
	assert.True(t, *a2.Optional)
	require.NotNil(t, a2.EnergySourceCode)
	assert.Equal(t, "SOLAR", *a2.EnergySourceCode)
}

func TestParseClassListCollection(t *testing.T) {
	data, err := os.ReadFile("../testdata/class_list.json")
	require.NoError(t, err)

	resp, err := parseODataCollection[MeasurementConceptClass](data)
	require.NoError(t, err)

	require.NotNil(t, resp.Count)
	assert.Equal(t, 2, *resp.Count)
	require.Len(t, resp.Items, 2)

	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", resp.Items[0].ID)
	require.NotNil(t, resp.Items[0].IDText)
	assert.Equal(t, "P_S", *resp.Items[0].IDText)
	require.NotNil(t, resp.Items[0].ClassTypeCode)
	assert.Equal(t, "CLASS", *resp.Items[0].ClassTypeCode)

	assert.Equal(t, "cccccccc-4444-5555-6666-777788889999", resp.Items[1].ID)
	require.NotNil(t, resp.Items[1].IDText)
	assert.Equal(t, "B_S", *resp.Items[1].IDText)
	require.NotNil(t, resp.Items[1].ClassTypeCode)
	assert.Equal(t, "SAPTEMPLATE", *resp.Items[1].ClassTypeCode)
}

// TestParseClassTypeCapabilityFlags verifies that the expanded classType
// (MCClassTypes) carries the readOnly / deletable / updateable capability
// flags exposed by the API (issue #28).
func TestParseClassTypeCapabilityFlags(t *testing.T) {
	raw := `{
		"id": "cccccccc-3333-4444-5555-666677778888",
		"classType": {
			"code": "SAPTEMPLATE",
			"name": "Template",
			"descr": "SAP Template",
			"readOnly": true,
			"deletable": false,
			"updateable": false
		}
	}`

	var cls MeasurementConceptClass
	require.NoError(t, json.Unmarshal([]byte(raw), &cls))

	require.NotNil(t, cls.ClassType)
	assert.Equal(t, "SAPTEMPLATE", cls.ClassType.Code)
	require.NotNil(t, cls.ClassType.ReadOnly)
	assert.True(t, *cls.ClassType.ReadOnly)
	require.NotNil(t, cls.ClassType.Deletable)
	assert.False(t, *cls.ClassType.Deletable)
	require.NotNil(t, cls.ClassType.Updateable)
	assert.False(t, *cls.ClassType.Updateable)
}
