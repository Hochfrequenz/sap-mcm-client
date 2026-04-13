package mcm

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestListOptionsQueryParamsNil(t *testing.T) {
	var opts *ListOptions
	qp := opts.queryParams()
	assert.Nil(t, qp)
}

func TestListOptionsQueryParamsEmpty(t *testing.T) {
	opts := &ListOptions{}
	qp := opts.queryParams()
	assert.NotNil(t, qp)
	assert.Empty(t, qp.Encode())
}

func TestListOptionsQueryParamsTop(t *testing.T) {
	top := 10
	opts := &ListOptions{Top: &top}
	qp := opts.queryParams()
	assert.Equal(t, "10", qp.Get("$top"))
}

func TestListOptionsQueryParamsSkip(t *testing.T) {
	skip := 20
	opts := &ListOptions{Skip: &skip}
	qp := opts.queryParams()
	assert.Equal(t, "20", qp.Get("$skip"))
}

func TestListOptionsQueryParamsCount(t *testing.T) {
	opts := &ListOptions{Count: true}
	qp := opts.queryParams()
	assert.Equal(t, "true", qp.Get("$count"))
}

func TestListOptionsQueryParamsCountFalse(t *testing.T) {
	opts := &ListOptions{Count: false}
	qp := opts.queryParams()
	assert.Empty(t, qp.Get("$count"))
}

func TestListOptionsQueryParamsOrderBy(t *testing.T) {
	opts := &ListOptions{OrderBy: "modifiedAt desc"}
	qp := opts.queryParams()
	assert.Equal(t, "modifiedAt desc", qp.Get("$orderby"))
}

func TestListOptionsQueryParamsSearch(t *testing.T) {
	opts := &ListOptions{Search: "electricity"}
	qp := opts.queryParams()
	assert.Equal(t, "electricity", qp.Get("$search"))
}

func TestListOptionsQueryParamsFilter(t *testing.T) {
	opts := &ListOptions{
		Filter: map[string]string{
			"division_code": "EL",
		},
	}
	qp := opts.queryParams()
	assert.Equal(t, "division_code eq 'EL'", qp.Get("$filter"))
}

func TestListOptionsQueryParamsFilterMultiple(t *testing.T) {
	opts := &ListOptions{
		Filter: map[string]string{
			"division_code":    "EL",
			"overallStatus_code": "ACTIVE",
		},
	}
	qp := opts.queryParams()
	filter := qp.Get("$filter")
	// Keys are sorted alphabetically, so division_code comes first.
	assert.Equal(t, "division_code eq 'EL' and overallStatus_code eq 'ACTIVE'", filter)
}

func TestListOptionsQueryParamsFilterEscapesSingleQuotes(t *testing.T) {
	opts := &ListOptions{
		Filter: map[string]string{
			"name": "it's a test",
		},
	}
	qp := opts.queryParams()
	filter := qp.Get("$filter")
	assert.Contains(t, filter, "it''s a test")
}

func TestListOptionsQueryParamsAll(t *testing.T) {
	top := 5
	skip := 10
	opts := &ListOptions{
		Top:     &top,
		Skip:    &skip,
		Count:   true,
		OrderBy: "modifiedAt desc",
		Search:  "test",
		Filter: map[string]string{
			"division_code": "GA",
		},
	}
	qp := opts.queryParams()
	assert.Equal(t, "5", qp.Get("$top"))
	assert.Equal(t, "10", qp.Get("$skip"))
	assert.Equal(t, "true", qp.Get("$count"))
	assert.Equal(t, "modifiedAt desc", qp.Get("$orderby"))
	assert.Equal(t, "test", qp.Get("$search"))
	assert.Equal(t, "division_code eq 'GA'", qp.Get("$filter"))
}

func TestDefaultInstanceExpandNonEmpty(t *testing.T) {
	expand := defaultInstanceExpand()
	assert.NotEmpty(t, expand)
	assert.Contains(t, expand, "meteringLocations")
	assert.Contains(t, expand, "marketLocations")
	assert.Contains(t, expand, "changeProcesses")
	assert.Contains(t, expand, "status")
}

func TestDefaultClassExpandNonEmpty(t *testing.T) {
	expand := defaultClassExpand()
	assert.NotEmpty(t, expand)
	assert.Contains(t, expand, "classType")
	assert.Contains(t, expand, "division")
	assert.Contains(t, expand, "meteringLocations")
	assert.Contains(t, expand, "actors")
}

func TestDefaultModelExpandNonEmpty(t *testing.T) {
	expand := defaultModelExpand()
	assert.NotEmpty(t, expand)
	assert.Contains(t, expand, "conceptType")
	assert.Contains(t, expand, "measurementClass")
	assert.Contains(t, expand, "status")
	assert.Contains(t, expand, "division")
	assert.Contains(t, expand, "marketLocations")
	assert.Contains(t, expand, "modelOperands")
}

func TestParseODataCollectionInstanceList(t *testing.T) {
	data, err := os.ReadFile("testdata/instance_list.json")
	require.NoError(t, err)

	resp, err := parseODataCollection[MeasurementConceptInstance](data)
	require.NoError(t, err)
	require.NotNil(t, resp)
	require.NotNil(t, resp.Count)
	assert.Equal(t, 2, *resp.Count)
	assert.Len(t, resp.Items, 2)
}

func TestParseODataCollectionInvalidJSON(t *testing.T) {
	_, err := parseODataCollection[MeasurementConceptInstance]([]byte(`not json`))
	assert.Error(t, err)
}

func TestParseODataCollectionEmptyValue(t *testing.T) {
	data := []byte(`{"value":[],"@odata.count":0}`)
	resp, err := parseODataCollection[MeasurementConceptInstance](data)
	require.NoError(t, err)
	require.NotNil(t, resp.Count)
	assert.Equal(t, 0, *resp.Count)
	assert.Empty(t, resp.Items)
}

func TestParseODataCollectionNoCount(t *testing.T) {
	data := []byte(`{"value":[]}`)
	resp, err := parseODataCollection[MeasurementConceptInstance](data)
	require.NoError(t, err)
	assert.Nil(t, resp.Count)
	assert.Empty(t, resp.Items)
}
