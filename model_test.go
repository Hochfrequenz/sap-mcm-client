package mcm

import (
	"encoding/json"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestParseModelGet(t *testing.T) {
	data, err := os.ReadFile("testdata/model_get.json")
	require.NoError(t, err)

	var model MeasurementConceptModel
	err = json.Unmarshal(data, &model)
	require.NoError(t, err)

	// Top-level fields
	assert.Equal(t, "ffffffff-2222-2222-2222-100000000001", model.ID)
	require.NotNil(t, model.IDText)
	assert.Equal(t, "B_S_M1", *model.IDText)
	require.NotNil(t, model.Name)
	assert.Equal(t, "Standard electricity model", *model.Name)
	require.NotNil(t, model.Description)
	assert.Equal(t, "Standard electricity model", *model.Description)
	require.NotNil(t, model.ExternalCode)
	assert.Equal(t, "986799345", *model.ExternalCode)
	require.NotNil(t, model.ConceptTypeCode)
	assert.Equal(t, "MODEL", *model.ConceptTypeCode)
	require.NotNil(t, model.MeasurementClassID)
	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", *model.MeasurementClassID)
	require.NotNil(t, model.StatusCode)
	assert.Equal(t, "ACTIVE", *model.StatusCode)
	require.NotNil(t, model.ValidFrom)
	assert.Equal(t, "2022-04-13", *model.ValidFrom)
	require.NotNil(t, model.ValidTo)
	assert.Equal(t, "9999-12-31", *model.ValidTo)
	require.NotNil(t, model.DivisionCode)
	assert.Equal(t, "EL", *model.DivisionCode)
	require.NotNil(t, model.Version)
	assert.Equal(t, "1", *model.Version)
	require.NotNil(t, model.CreatedAt)
	assert.Equal(t, 2022, model.CreatedAt.Year())
	require.NotNil(t, model.ModifiedAt)
	assert.Equal(t, 2022, model.ModifiedAt.Year())
}

func TestParseModelGetExpandedTypes(t *testing.T) {
	data, err := os.ReadFile("testdata/model_get.json")
	require.NoError(t, err)

	var model MeasurementConceptModel
	err = json.Unmarshal(data, &model)
	require.NoError(t, err)

	// ConceptType
	require.NotNil(t, model.ConceptType)
	assert.Equal(t, "MODEL", model.ConceptType.Code)
	require.NotNil(t, model.ConceptType.Name)
	assert.Equal(t, "Model", *model.ConceptType.Name)

	// Status
	require.NotNil(t, model.Status)
	assert.Equal(t, "ACTIVE", model.Status.Code)
	require.NotNil(t, model.Status.Name)
	assert.Equal(t, "Active", *model.Status.Name)

	// Division
	require.NotNil(t, model.Division)
	assert.Equal(t, "EL", model.Division.Code)
	require.NotNil(t, model.Division.Name)
	assert.Equal(t, "Electricity", *model.Division.Name)

	// MeasurementClass
	require.NotNil(t, model.MeasurementClass)
	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", model.MeasurementClass.ID)
	require.NotNil(t, model.MeasurementClass.Name)
	assert.Equal(t, "Feed-in with unmetered generating plant", *model.MeasurementClass.Name)
}

func TestParseModelGetMarketLocations(t *testing.T) {
	data, err := os.ReadFile("testdata/model_get.json")
	require.NoError(t, err)

	var model MeasurementConceptModel
	err = json.Unmarshal(data, &model)
	require.NoError(t, err)

	require.Len(t, model.MarketLocations, 1)
	ml := model.MarketLocations[0]
	assert.Equal(t, "aaaaaaaa-2222-3333-1111-100000000001", ml.ID)
	require.NotNil(t, ml.IDText)
	assert.Equal(t, "MaLo_VB", *ml.IDText)
	require.NotNil(t, ml.TypeCode)
	assert.Equal(t, "SUPPLY", *ml.TypeCode)
	require.NotNil(t, ml.VirtualMarketLocation)
	assert.False(t, *ml.VirtualMarketLocation)
	require.NotNil(t, ml.DirectionCode)
	assert.Equal(t, "OUT", *ml.DirectionCode)
	require.NotNil(t, ml.Position)
	assert.Equal(t, 1, *ml.Position)

	// Actors mapping
	require.Len(t, ml.ActorsMapping, 1)
	am := ml.ActorsMapping[0]
	assert.Equal(t, "aaaaaaaa-3333-4444-5555-100000000001", am.ID)
	assert.Equal(t, "VB1", am.ActorIDText)
	require.NotNil(t, am.ActorDirectionCode)
	assert.Equal(t, "OUT", *am.ActorDirectionCode)
	require.NotNil(t, am.ActorTypeCode)
	assert.Equal(t, "CONSUMER", *am.ActorTypeCode)

	// Calculation rules
	require.Len(t, ml.CalculationRules, 1)
	cr := ml.CalculationRules[0]
	assert.Equal(t, "ffff1111-2222-3333-1111-100000000001", cr.ID)
	require.NotNil(t, cr.MeteringProcedureCode)
	assert.Equal(t, "SLP", *cr.MeteringProcedureCode)

	// Usages on calculation rule
	require.Len(t, cr.Usages, 2)
	require.NotNil(t, cr.Usages[0].UsageCode)
	assert.Equal(t, "GRIDUSE", *cr.Usages[0].UsageCode)
	require.NotNil(t, cr.Usages[1].UsageCode)
	assert.Equal(t, "OUBILL", *cr.Usages[1].UsageCode)
}

func TestParseModelGetOperands(t *testing.T) {
	data, err := os.ReadFile("testdata/model_get.json")
	require.NoError(t, err)

	var model MeasurementConceptModel
	err = json.Unmarshal(data, &model)
	require.NoError(t, err)

	require.Len(t, model.ModelOperands, 1)
	op := model.ModelOperands[0]
	assert.Equal(t, "dddd1111-2222-3333-4444-100000000001", op.ID)
	require.NotNil(t, op.Operand)
	assert.Equal(t, "Z1B", *op.Operand)
	require.NotNil(t, op.MeteringTaskID)
	assert.Equal(t, "bbb50001-5555-5555-5555-501010000001", *op.MeteringTaskID)
	require.NotNil(t, op.MeteringTaskTypeCode)
	assert.Equal(t, "AE", *op.MeteringTaskTypeCode)
	require.NotNil(t, op.MeteringTaskDirectionCode)
	assert.Equal(t, "OUT", *op.MeteringTaskDirectionCode)
	assert.Equal(t, "Z1", op.MeteringLocationIDText)
}

func TestParseModelGetMeteringLocationPurposes(t *testing.T) {
	data, err := os.ReadFile("testdata/model_get.json")
	require.NoError(t, err)

	var model MeasurementConceptModel
	err = json.Unmarshal(data, &model)
	require.NoError(t, err)

	require.Len(t, model.MeteringLocationPurposes, 1)
	p := model.MeteringLocationPurposes[0]
	assert.Equal(t, "eeee1111-2222-3333-4444-100000000001", p.ID)
	require.NotNil(t, p.MeteringLocationTypeCode)
	assert.Equal(t, "GRIDMES", *p.MeteringLocationTypeCode)
	assert.Equal(t, "Z1", p.MeteringLocationIDText)
	require.NotNil(t, p.PurposeCode)
	assert.Equal(t, "SC", *p.PurposeCode)
}

func TestParseModelListCollection(t *testing.T) {
	data, err := os.ReadFile("testdata/model_list.json")
	require.NoError(t, err)

	resp, err := parseODataCollection[MeasurementConceptModel](data)
	require.NoError(t, err)

	require.NotNil(t, resp.Count)
	assert.Equal(t, 2, *resp.Count)
	require.Len(t, resp.Items, 2)

	assert.Equal(t, "ffffffff-2222-2222-2222-100000000001", resp.Items[0].ID)
	require.NotNil(t, resp.Items[0].IDText)
	assert.Equal(t, "B_S_M1", *resp.Items[0].IDText)
	require.NotNil(t, resp.Items[0].StatusCode)
	assert.Equal(t, "ACTIVE", *resp.Items[0].StatusCode)
	require.NotNil(t, resp.Items[0].DivisionCode)
	assert.Equal(t, "EL", *resp.Items[0].DivisionCode)

	assert.Equal(t, "ffffffff-3333-3333-3333-200000000001", resp.Items[1].ID)
	require.NotNil(t, resp.Items[1].IDText)
	assert.Equal(t, "B_S_M2", *resp.Items[1].IDText)
	require.NotNil(t, resp.Items[1].StatusCode)
	assert.Equal(t, "IN_PROGRESS", *resp.Items[1].StatusCode)
	require.NotNil(t, resp.Items[1].DivisionCode)
	assert.Equal(t, "GA", *resp.Items[1].DivisionCode)
}
