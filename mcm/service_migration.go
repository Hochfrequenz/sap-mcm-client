package mcm

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

// MigrationService handles communication with the Measurement Concept
// Instance Migration API endpoints.
//
// Unlike the other services, MigrationService targets a separate OData path
// (/odata/v4/api/migrate/v1) but shares the same authentication and HTTP
// client as the rest of the MCM API.
type MigrationService struct {
	client *Client
}

// ListStagedOptions holds the parameters accepted by
// MigrationService.ListStaged.
type ListStagedOptions struct {
	// RequestID filters by the migration request UUID returned by Migrate.
	// When empty no filter is applied.
	RequestID string
	// Status filters by the migration status code. When empty no filter is applied.
	Status string
	// Top limits the number of returned staged entries ($top).
	Top *int
	// Count requests an inline total count ($count=true).
	Count bool
	// IncludeInstance expands the "instance" navigation property so that each
	// returned StagedMigrationInstance carries the full migrated measurement
	// concept instance.
	IncludeInstance bool
}

// url builds the full migration endpoint URL for a given relative path.
func (s *MigrationService) url(path string) string {
	return s.client.rawBaseURL + migrationBasePath + "/" + strings.TrimLeft(path, "/")
}

// Migrate submits a batch of measurement concept instances for migration.
//
// Corresponds to POST /odata/v4/api/migrate/v1/migrate. The endpoint wraps
// the given instances in the required {"migrationInstances": [...]} body and
// returns the request identifier assigned to the batch.
func (s *MigrationService) Migrate(ctx context.Context, instances []MigrationInstance) (*MigrationResponse, error) {
	payload := MigrationInstancesRequest{MigrationInstances: instances}

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodPost, s.url("migrate"), &payload)
	if err != nil {
		return nil, err
	}

	var result MigrationResponse
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// Get retrieves a single migration instance by ID.
//
// Corresponds to GET /odata/v4/api/migrate/v1/MigrationInstances({id}).
// All sub-collections are expanded using the default migration expand set
// (change processes, status, metering locations & tasks, actors, market
// locations with calculation rules + usages + actors, addresses, and
// operand mappings).
func (s *MigrationService) Get(ctx context.Context, instanceID string) (*MigrationInstanceResponse, error) {
	path := fmt.Sprintf("MigrationInstances(%s)?$expand=%s", instanceID, url.QueryEscape(defaultMigrationExpand()))

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodGet, s.url(path), nil)
	if err != nil {
		return nil, err
	}

	var result MigrationInstanceResponse
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// ListStaged retrieves staged migration instances matching the given options.
//
// Corresponds to GET /odata/v4/api/migrate/v1/StagedMigrationInstances with
// optional $filter, $top, $count, and $expand system query options.
func (s *MigrationService) ListStaged(ctx context.Context, opts *ListStagedOptions) (*ListResponse[StagedMigrationInstance], error) {
	qp := url.Values{}
	var clauses []string

	if opts != nil {
		if opts.RequestID != "" {
			// OData V4 Guid literals are unquoted.
			clauses = append(clauses, "requestId eq "+opts.RequestID)
		}
		if opts.Status != "" {
			escaped := strings.ReplaceAll(opts.Status, "'", "''")
			clauses = append(clauses, "status_code eq '"+escaped+"'")
		}
		if opts.Top != nil {
			qp.Set("$top", strconv.Itoa(*opts.Top))
		}
		if opts.Count {
			qp.Set("$count", "true")
		}
		if opts.IncludeInstance {
			qp.Set("$expand", "instance")
		}
	}
	if len(clauses) > 0 {
		qp.Set("$filter", strings.Join(clauses, " and "))
	}

	path := "StagedMigrationInstances"
	if encoded := qp.Encode(); encoded != "" {
		path += "?" + encoded
	}

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodGet, s.url(path), nil)
	if err != nil {
		return nil, err
	}

	body, err := s.client.doRaw(req)
	if err != nil {
		return nil, err
	}
	return parseODataCollection[StagedMigrationInstance](body)
}

// Purge deletes the staged migration data identified by the given migration
// request ID (as returned by Migrate).
//
// Corresponds to POST /odata/v4/api/migrate/v1/purge.
func (s *MigrationService) Purge(ctx context.Context, requestID string) error {
	payload := PurgeRequest{RequestID: requestID}

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodPost, s.url("purge"), &payload)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// CheckProgress returns the migration progress of the measurement concept
// instance identified by instanceID.
//
// Corresponds to GET
// /odata/v4/api/migrate/v1/MigrationInstances({id})/MCMMigrationService.checkProgress.
func (s *MigrationService) CheckProgress(ctx context.Context, instanceID string) (*ProcessProgress, error) {
	path := fmt.Sprintf("MigrationInstances(%s)/MCMMigrationService.checkProgress", instanceID)

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodGet, s.url(path), nil)
	if err != nil {
		return nil, err
	}

	var result ProcessProgress
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// CheckChangeProcessProgress returns the migration progress of the change
// process identified by changeProcessID.
//
// Corresponds to GET
// /odata/v4/api/migrate/v1/MIGChangeProcesses({id})/MCMMigrationService.checkProgress.
func (s *MigrationService) CheckChangeProcessProgress(ctx context.Context, changeProcessID string) (*ProcessProgress, error) {
	path := fmt.Sprintf("MIGChangeProcesses(%s)/MCMMigrationService.checkProgress", changeProcessID)

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodGet, s.url(path), nil)
	if err != nil {
		return nil, err
	}

	var result ProcessProgress
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// defaultMigrationExpand returns the full $expand string for migration
// instances, mirroring the expansions documented in the Migration API spec.
func defaultMigrationExpand() string {
	return "changeProcesses," +
		"status," +
		"meteringLocations($expand=meteringTasks)," +
		"actors," +
		"marketLocations($expand=calculationRules($expand=usages),actors)," +
		"addresses," +
		"operandMappings"
}
