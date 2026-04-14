//nolint:dupl // intentional - read-only services (Classes/Models) share structure
package mcm

import (
	"context"
	"fmt"
	"net/http"
)

// ClassService handles communication with the measurement concept class
// related endpoints of the SAP MCM API.
type ClassService struct {
	client *Client
}

// List retrieves a paginated list of measurement concept classes.
// Pass nil for opts to use default pagination.
func (s *ClassService) List(ctx context.Context, opts *ListOptions) (*ListResponse[MeasurementConceptClass], error) {
	qp := opts.queryParams()
	if qp == nil {
		qp = make(map[string][]string)
	}
	qp.Set("$expand", defaultClassExpand())

	path := "MeasurementConceptClasses?" + qp.Encode()

	req, err := s.client.newRequest(ctx, http.MethodGet, path, nil)
	if err != nil {
		return nil, err
	}

	body, err := s.client.doRaw(req)
	if err != nil {
		return nil, err
	}

	return parseODataCollection[MeasurementConceptClass](body)
}

// Get retrieves a single measurement concept class by ID.
func (s *ClassService) Get(ctx context.Context, id string) (*MeasurementConceptClass, error) {
	path := fmt.Sprintf("MeasurementConceptClasses(%s)?$expand=%s", id, defaultClassExpand())

	req, err := s.client.newRequest(ctx, http.MethodGet, path, nil)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptClass
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}
