package mcm

import (
	"context"
	"fmt"
	"net/http"
)

// ModelService handles communication with the measurement concept model
// related endpoints of the SAP MCM API.
type ModelService struct {
	client *Client
}

// List retrieves a paginated list of measurement concept models.
// Pass nil for opts to use default pagination.
func (s *ModelService) List(ctx context.Context, opts *ListOptions) (*ListResponse[MeasurementConceptModel], error) {
	qp := opts.queryParams()
	if qp == nil {
		qp = make(map[string][]string)
	}
	qp.Set("$expand", defaultModelExpand())

	path := "MeasurementConceptModels?" + qp.Encode()

	req, err := s.client.newRequest(ctx, http.MethodGet, path, nil)
	if err != nil {
		return nil, err
	}

	body, err := s.client.doRaw(req)
	if err != nil {
		return nil, err
	}

	return parseODataCollection[MeasurementConceptModel](body)
}

// Get retrieves a single measurement concept model by ID.
func (s *ModelService) Get(ctx context.Context, id string) (*MeasurementConceptModel, error) {
	path := fmt.Sprintf("MeasurementConceptModels(%s)?$expand=%s", id, defaultModelExpand())

	req, err := s.client.newRequest(ctx, http.MethodGet, path, nil)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptModel
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}
