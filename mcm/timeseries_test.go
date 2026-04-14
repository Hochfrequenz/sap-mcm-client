package mcm

import (
	"encoding/json"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// timeSeriesEnvelopeFromFixture is a tiny test-only wrapper that parses the
// OData V4 collection response used in testdata/timeseries_data.json.
type timeSeriesEnvelopeFromFixture struct {
	Value []TimeSeriesDataPoint `json:"value"`
}

func TestParseTimeSeriesDataCollection(t *testing.T) {
	data, err := os.ReadFile("../testdata/timeseries_data.json")
	require.NoError(t, err)

	var env timeSeriesEnvelopeFromFixture
	require.NoError(t, json.Unmarshal(data, &env))
	require.Len(t, env.Value, 4)

	p0 := env.Value[0]
	assert.Equal(t, "0aa18b64-1111-4bbb-ae00-000000000001", p0.ID)
	assert.Equal(t, "imp-20260101-0001", p0.ImportID)
	assert.Equal(t, "UTC", p0.TimeZoneCode)
	assert.Equal(t, "MEASURED", p0.Quality)
	assert.Equal(t, "123e4567-e89b-12d3-a456-426614174000", p0.TimeSeriesID)
	assert.Equal(t, "1+1-1:1.29.0", p0.ExternalID)
	assert.False(t, p0.Missing)
	assert.Equal(t, 2026, p0.Timestamp.Year())

	// Decimal handling: IEEE754Compatible=true serialises as string.
	require.NotNil(t, p0.Value)
	assert.Equal(t, "42.500", p0.Value.String())
}

func TestParseTimeSeriesDataMissingPoint(t *testing.T) {
	data, err := os.ReadFile("../testdata/timeseries_data.json")
	require.NoError(t, err)

	var env timeSeriesEnvelopeFromFixture
	require.NoError(t, json.Unmarshal(data, &env))
	require.Len(t, env.Value, 4)

	// Entry [2] has missing=true and a null value.
	p := env.Value[2]
	assert.True(t, p.Missing)
	assert.Nil(t, p.Value)
	assert.Equal(t, "ESTIMATED", p.Quality)
}

func TestParseTimeSeriesDataDecimalPrecision(t *testing.T) {
	data, err := os.ReadFile("../testdata/timeseries_data.json")
	require.NoError(t, err)

	var env timeSeriesEnvelopeFromFixture
	require.NoError(t, json.Unmarshal(data, &env))

	require.NotNil(t, env.Value[1].Value)
	assert.Equal(t, "43.125", env.Value[1].Value.String())
	require.NotNil(t, env.Value[3].Value)
	assert.Equal(t, "41.750", env.Value[3].Value.String())
}

func TestDeleteTimeSeriesRequestMarshal(t *testing.T) {
	start := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	end := time.Date(2026, 1, 31, 0, 0, 0, 0, time.UTC)

	req := DeleteTimeSeriesRequest{
		UUIDs:       []string{"123e4567-e89b-12d3-a456-426614174000"},
		ExternalIDs: []string{"1+1-1:1.29.0"},
		StartTime:   start,
		EndTime:     end,
	}

	body, err := json.Marshal(&req)
	require.NoError(t, err)

	var round map[string]any
	require.NoError(t, json.Unmarshal(body, &round))
	assert.Contains(t, round, "uuids")
	assert.Contains(t, round, "externalIds")
	assert.Contains(t, round, "startTime")
	assert.Contains(t, round, "endTime")
}

func TestDeleteTimeSeriesRequestMarshalOmitsEmptyLists(t *testing.T) {
	// Only UUIDs set → externalIds must be omitted (omitempty tag).
	req := DeleteTimeSeriesRequest{
		UUIDs:     []string{"123e4567-e89b-12d3-a456-426614174000"},
		StartTime: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
		EndTime:   time.Date(2026, 1, 31, 0, 0, 0, 0, time.UTC),
	}
	body, err := json.Marshal(&req)
	require.NoError(t, err)
	var round map[string]any
	require.NoError(t, json.Unmarshal(body, &round))
	assert.Contains(t, round, "uuids")
	assert.NotContains(t, round, "externalIds")
}
