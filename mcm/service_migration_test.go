package mcm

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ---------------------------------------------------------------------------
// Migrate
// ---------------------------------------------------------------------------

func TestMigrationMigratePostsWrapperBody(t *testing.T) {
	respFixture, err := os.ReadFile("../testdata/migration_response.json")
	require.NoError(t, err)

	var gotMethod, gotPath string
	var gotBody []byte
	var gotContentType string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		gotPath = r.URL.Path
		gotContentType = r.Header.Get("Content-Type")
		var err error
		gotBody, err = io.ReadAll(r.Body)
		require.NoError(t, err)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		_, _ = w.Write(respFixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)

	inst := MigrationInstance{
		ID:     "b2c3d4e5-f6a7-8901-bcde-f12345678901",
		IDText: "MIG-INST-LEGACY-001",
	}
	resp, err := c.Migration.Migrate(context.Background(), []MigrationInstance{inst})
	require.NoError(t, err)
	require.NotNil(t, resp)
	assert.Equal(t, "f1343cac-b0ee-42aa-af23-43b1f628f61d", resp.RequestID)

	assert.Equal(t, http.MethodPost, gotMethod)
	assert.Equal(t, "/odata/v4/api/migrate/v1/migrate", gotPath)
	assert.Equal(t, odataContentType, gotContentType)

	// Verify the body is wrapped in {"migrationInstances": [...]}.
	var body map[string]any
	require.NoError(t, json.Unmarshal(gotBody, &body))
	arr, ok := body["migrationInstances"].([]any)
	require.True(t, ok, "migrationInstances must be an array")
	require.Len(t, arr, 1)

	first, ok := arr[0].(map[string]any)
	require.True(t, ok)
	assert.Equal(t, "MIG-INST-LEGACY-001", first["idText"])
	assert.Equal(t, "b2c3d4e5-f6a7-8901-bcde-f12345678901", first["id"])
}

func TestMigrationMigrateWithEmptyList(t *testing.T) {
	respFixture, err := os.ReadFile("../testdata/migration_response.json")
	require.NoError(t, err)

	var gotBody []byte
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotBody, _ = io.ReadAll(r.Body)
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(respFixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	_, err = c.Migration.Migrate(context.Background(), nil)
	require.NoError(t, err)

	// Even with a nil slice, the wrapper is present.
	var body map[string]any
	require.NoError(t, json.Unmarshal(gotBody, &body))
	assert.Contains(t, body, "migrationInstances")
}

// ---------------------------------------------------------------------------
// Get
// ---------------------------------------------------------------------------

func TestMigrationGetConstructsURLWithExpand(t *testing.T) {
	respFixture, err := os.ReadFile("../testdata/migration_instance_get.json")
	require.NoError(t, err)

	var gotPath, gotRawQuery string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotPath = r.URL.Path
		gotRawQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(respFixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	id := "b2c3d4e5-f6a7-8901-bcde-f12345678901"
	inst, err := c.Migration.Get(context.Background(), id)
	require.NoError(t, err)
	require.NotNil(t, inst)
	assert.Equal(t, id, inst.ID)
	assert.Equal(t, "MIG-INST-LEGACY-001", inst.IDText)

	assert.Equal(t, "/odata/v4/api/migrate/v1/MigrationInstances("+id+")", gotPath)
	decoded, err := url.QueryUnescape(gotRawQuery)
	require.NoError(t, err)
	// Full default expand should be present.
	assert.Contains(t, decoded, "$expand=")
	assert.Contains(t, decoded, "changeProcesses")
	assert.Contains(t, decoded, "status")
	assert.Contains(t, decoded, "meteringLocations($expand=meteringTasks)")
	assert.Contains(t, decoded, "actors")
	assert.Contains(t, decoded, "marketLocations($expand=calculationRules($expand=usages),actors)")
	assert.Contains(t, decoded, "addresses")
	assert.Contains(t, decoded, "operandMappings")
}

// ---------------------------------------------------------------------------
// ListStaged
// ---------------------------------------------------------------------------

func TestMigrationListStagedBasic(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/migration_staged_list.json")
	require.NoError(t, err)

	var gotPath, gotRawQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotPath = r.URL.Path
		gotRawQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)

	top := 10
	resp, err := c.Migration.ListStaged(context.Background(), &ListStagedOptions{Top: &top, Count: true})
	require.NoError(t, err)
	require.NotNil(t, resp)
	require.NotNil(t, resp.Count)
	assert.Equal(t, 3, *resp.Count)
	require.Len(t, resp.Items, 3)

	assert.Equal(t, "/odata/v4/api/migrate/v1/StagedMigrationInstances", gotPath)
	decoded, err := url.QueryUnescape(gotRawQuery)
	require.NoError(t, err)
	assert.Contains(t, decoded, "$top=10")
	assert.Contains(t, decoded, "$count=true")
}

func TestMigrationListStagedRequestIDFilter(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/migration_staged_list.json")
	require.NoError(t, err)

	var gotRawQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotRawQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	requestID := "f1343cac-b0ee-42aa-af23-43b1f628f61d"
	_, err = c.Migration.ListStaged(context.Background(), &ListStagedOptions{
		RequestID: requestID,
	})
	require.NoError(t, err)

	decoded, err := url.QueryUnescape(gotRawQuery)
	require.NoError(t, err)
	// OData V4 Guid literals are unquoted.
	assert.Contains(t, decoded, "$filter=requestId eq "+requestID)
}

func TestMigrationListStagedStatusFilter(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/migration_staged_list.json")
	require.NoError(t, err)

	var gotRawQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotRawQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	_, err = c.Migration.ListStaged(context.Background(), &ListStagedOptions{
		Status: "MIGRATED",
	})
	require.NoError(t, err)

	decoded, err := url.QueryUnescape(gotRawQuery)
	require.NoError(t, err)
	assert.Contains(t, decoded, "$filter=status_code eq 'MIGRATED'")
}

func TestMigrationListStagedIncludeInstance(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/migration_staged_list.json")
	require.NoError(t, err)

	var gotRawQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotRawQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	_, err = c.Migration.ListStaged(context.Background(), &ListStagedOptions{
		IncludeInstance: true,
	})
	require.NoError(t, err)

	decoded, err := url.QueryUnescape(gotRawQuery)
	require.NoError(t, err)
	assert.Contains(t, decoded, "$expand=instance")
}

func TestMigrationListStagedCombinedFilters(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/migration_staged_list.json")
	require.NoError(t, err)

	var gotRawQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotRawQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	top := 5
	requestID := "f1343cac-b0ee-42aa-af23-43b1f628f61d"
	_, err = c.Migration.ListStaged(context.Background(), &ListStagedOptions{
		RequestID:       requestID,
		Status:          "FAILED",
		Top:             &top,
		Count:           true,
		IncludeInstance: true,
	})
	require.NoError(t, err)

	decoded, err := url.QueryUnescape(gotRawQuery)
	require.NoError(t, err)
	assert.Contains(t, decoded, "requestId eq "+requestID)
	assert.Contains(t, decoded, "status_code eq 'FAILED'")
	assert.Contains(t, decoded, " and ")
	assert.Contains(t, decoded, "$top=5")
	assert.Contains(t, decoded, "$count=true")
	assert.Contains(t, decoded, "$expand=instance")
}

func TestMigrationListStagedNilOptions(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/migration_staged_list.json")
	require.NoError(t, err)

	var gotPath string
	var gotRawQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotPath = r.URL.Path
		gotRawQuery = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	resp, err := c.Migration.ListStaged(context.Background(), nil)
	require.NoError(t, err)
	require.Len(t, resp.Items, 3)
	assert.Equal(t, "/odata/v4/api/migrate/v1/StagedMigrationInstances", gotPath)
	assert.Empty(t, gotRawQuery)
}

// ---------------------------------------------------------------------------
// Error propagation
// ---------------------------------------------------------------------------

func TestMigrationGet404(t *testing.T) {
	errFixture, err := os.ReadFile("../testdata/error_404.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write(errFixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	_, err = c.Migration.Get(context.Background(), "00000000-0000-0000-0000-000000000000")
	require.Error(t, err)
	assert.True(t, IsNotFound(err))
}

func TestMigrationMigrate401(t *testing.T) {
	errFixture, err := os.ReadFile("../testdata/error_401.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write(errFixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	_, err = c.Migration.Migrate(context.Background(), []MigrationInstance{})
	require.Error(t, err)
	assert.True(t, IsUnauthorized(err))
}

func TestMigrationListStaged403(t *testing.T) {
	errFixture, err := os.ReadFile("../testdata/error_403.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusForbidden)
		_, _ = w.Write(errFixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	_, err = c.Migration.ListStaged(context.Background(), nil)
	require.Error(t, err)
	assert.True(t, IsForbidden(err))
}

// ---------------------------------------------------------------------------
// Purge / CheckProgress (issue #24)
// ---------------------------------------------------------------------------

func TestMigrationPurgePostsRequestID(t *testing.T) {
	var gotMethod, gotPath string
	var gotBody []byte

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		gotPath = r.URL.Path
		gotBody, _ = io.ReadAll(r.Body)
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	require.NoError(t, c.Migration.Purge(context.Background(), "f1343cac-b0ee-42aa-af23-43b1f628f61d"))

	assert.Equal(t, http.MethodPost, gotMethod)
	assert.Equal(t, "/odata/v4/api/migrate/v1/purge", gotPath)

	var body map[string]any
	require.NoError(t, json.Unmarshal(gotBody, &body))
	assert.Equal(t, "f1343cac-b0ee-42aa-af23-43b1f628f61d", body["requestId"])
}

func TestMigrationCheckProgress(t *testing.T) {
	var gotMethod, gotPath string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		gotPath = r.URL.Path
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{
			"changeProcessId": "aaaaaaaa-bbbb-cccc-dddd-000000000001",
			"instanceId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
			"instanceIdText": "MIG-INST-LEGACY-001",
			"instanceVersion": "1",
			"currentStatus": {"instanceStatus": "STAGED", "processStatus": "IN_PROGRESS"},
			"nextStatus": {"instanceStatus": "ACTIVE", "processStatus": "DONE"},
			"failedValidations": [
				{"name": "missingActor", "position": 2, "parameters": ["actor", "MELO1"]}
			]
		}`))
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	progress, err := c.Migration.CheckProgress(context.Background(), "b2c3d4e5-f6a7-8901-bcde-f12345678901")
	require.NoError(t, err)
	require.NotNil(t, progress)

	assert.Equal(t, http.MethodGet, gotMethod)
	assert.Equal(t, "/odata/v4/api/migrate/v1/MigrationInstances(b2c3d4e5-f6a7-8901-bcde-f12345678901)/MCMMigrationService.checkProgress", gotPath)

	assert.Equal(t, "MIG-INST-LEGACY-001", progress.InstanceIDText)
	require.NotNil(t, progress.CurrentStatus)
	require.NotNil(t, progress.CurrentStatus.InstanceStatus)
	assert.Equal(t, "STAGED", *progress.CurrentStatus.InstanceStatus)
	require.Len(t, progress.FailedValidations, 1)
	require.NotNil(t, progress.FailedValidations[0].Name)
	assert.Equal(t, "missingActor", *progress.FailedValidations[0].Name)
	assert.Equal(t, []string{"actor", "MELO1"}, progress.FailedValidations[0].Parameters)
}

func TestMigrationCheckChangeProcessProgress(t *testing.T) {
	var gotPath string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotPath = r.URL.Path
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"changeProcessId": "aaaaaaaa-bbbb-cccc-dddd-000000000001", "instanceId": "", "instanceIdText": "", "instanceVersion": ""}`))
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	progress, err := c.Migration.CheckChangeProcessProgress(context.Background(), "aaaaaaaa-bbbb-cccc-dddd-000000000001")
	require.NoError(t, err)
	require.NotNil(t, progress)

	assert.Equal(t, "/odata/v4/api/migrate/v1/MIGChangeProcesses(aaaaaaaa-bbbb-cccc-dddd-000000000001)/MCMMigrationService.checkProgress", gotPath)
	assert.Equal(t, "aaaaaaaa-bbbb-cccc-dddd-000000000001", progress.ChangeProcessID)
}
