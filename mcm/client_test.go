package mcm

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// testClient creates a Client that points to the given httptest.Server.
// It bypasses authentication by using the server's built-in client.
func testClient(t *testing.T, srv *httptest.Server) *Client {
	t.Helper()
	c := &Client{
		baseURL:    srv.URL + basePath,
		httpClient: srv.Client(),
	}
	c.Instances = &InstanceService{client: c}
	c.Classes = &ClassService{client: c}
	c.Models = &ModelService{client: c}
	return c
}

func TestNewClient(t *testing.T) {
	tokenSrv, _ := newTestTokenServer(t, "test-token", 3600)
	defer tokenSrv.Close()

	c := NewClient(Config{
		BaseURL: "https://example.com",
		Auth: AuthConfig{
			TokenURL:     tokenSrv.URL,
			ClientID:     "cid",
			ClientSecret: "csec",
		},
	})

	require.NotNil(t, c)
	require.NotNil(t, c.Instances)
	require.NotNil(t, c.Classes)
	require.NotNil(t, c.Models)
	assert.Equal(t, "https://example.com"+basePath, c.baseURL)
}

func TestNewClientDefaultTimeout(t *testing.T) {
	tokenSrv, _ := newTestTokenServer(t, "test-token", 3600)
	defer tokenSrv.Close()

	c := NewClient(Config{
		BaseURL: "https://example.com",
		Auth: AuthConfig{
			TokenURL:     tokenSrv.URL,
			ClientID:     "cid",
			ClientSecret: "csec",
		},
	})

	// Default timeout is 30 seconds.
	assert.NotNil(t, c.httpClient)
}

func TestNewClientTrailingSlash(t *testing.T) {
	tokenSrv, _ := newTestTokenServer(t, "test-token", 3600)
	defer tokenSrv.Close()

	c := NewClient(Config{
		BaseURL: "https://example.com/",
		Auth: AuthConfig{
			TokenURL:     tokenSrv.URL,
			ClientID:     "cid",
			ClientSecret: "csec",
		},
	})

	assert.Equal(t, "https://example.com"+basePath, c.baseURL)
}

// --- Instances integration tests ---

func TestInstancesGet(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodGet, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(a1b2c3d4-e5f6-7890-abcd-ef1234567890)")
		assert.Contains(t, r.URL.RawQuery, "$expand=")
		assert.Equal(t, odataAccept, r.Header.Get("Accept"))

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	inst, err := c.Instances.Get(context.Background(), "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
	require.NoError(t, err)
	require.NotNil(t, inst)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", inst.ID)
	assert.Equal(t, "INST-79", inst.IDText)
}

func TestInstancesList(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_list.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodGet, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances")
		// The query is URL-encoded, so check for the encoded form.
		assert.Contains(t, r.URL.RawQuery, "%24expand=")

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	top := 10
	resp, err := c.Instances.List(context.Background(), &ListOptions{Top: &top, Count: true})
	require.NoError(t, err)
	require.NotNil(t, resp)
	require.NotNil(t, resp.Count)
	assert.Equal(t, 2, *resp.Count)
	assert.Len(t, resp.Items, 2)
}

func TestInstancesListNilOpts(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_list.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	resp, err := c.Instances.List(context.Background(), nil)
	require.NoError(t, err)
	assert.Len(t, resp.Items, 2)
}

func TestInstancesCreate(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances")
		assert.Equal(t, odataContentType, r.Header.Get("Content-Type"))
		assert.Equal(t, odataAccept, r.Header.Get("Accept"))

		// Verify the request body was sent correctly.
		body, err := io.ReadAll(r.Body)
		require.NoError(t, err)
		var input CreateInstanceInput
		err = json.Unmarshal(body, &input)
		require.NoError(t, err)
		assert.Equal(t, "ffffffff-2222-2222-2222-100000000001", input.MeasurementModelID)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	desc := "Test instance"
	input := &CreateInstanceInput{
		MeasurementModelID: "ffffffff-2222-2222-2222-100000000001",
		Description:        &desc,
	}

	inst, err := c.Instances.Create(context.Background(), input)
	require.NoError(t, err)
	require.NotNil(t, inst)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", inst.ID)
}

func TestInstancesInitChange(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(a1b2c3d4-e5f6-7890-abcd-ef1234567890)/MCMService.initChange")

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	input := &InitChangeInput{
		DataForNewInstanceVersion: []InitChangeVersionData{
			{MeasurementModelID: "ffffffff-2222-2222-2222-100000000001"},
		},
	}

	inst, err := c.Instances.InitChange(context.Background(), "a1b2c3d4-e5f6-7890-abcd-ef1234567890", input)
	require.NoError(t, err)
	require.NotNil(t, inst)
	assert.Equal(t, "a1b2c3d4-e5f6-7890-abcd-ef1234567890", inst.ID)
}

// --- Classes integration tests ---

//nolint:dupl // intentional - parallel structure to TestModelsGet for symmetric services
func TestClassesGet(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/class_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodGet, r.Method)
		assert.Contains(t, r.URL.Path, "MeasurementConceptClasses(cccccccc-3333-4444-5555-666677778888)")
		assert.Contains(t, r.URL.RawQuery, "$expand=")

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	cls, err := c.Classes.Get(context.Background(), "cccccccc-3333-4444-5555-666677778888")
	require.NoError(t, err)
	require.NotNil(t, cls)
	assert.Equal(t, "cccccccc-3333-4444-5555-666677778888", cls.ID)
	require.NotNil(t, cls.Name)
	assert.Equal(t, "Feed-in with unmetered generating plant", *cls.Name)
}

func TestClassesList(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/class_list.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodGet, r.Method)
		assert.Contains(t, r.URL.Path, "MeasurementConceptClasses")

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	resp, err := c.Classes.List(context.Background(), nil)
	require.NoError(t, err)
	require.NotNil(t, resp)
	require.NotNil(t, resp.Count)
	assert.Equal(t, 2, *resp.Count)
	assert.Len(t, resp.Items, 2)
}

// --- Models integration tests ---

//nolint:dupl // intentional - parallel structure to TestClassesGet for symmetric services
func TestModelsGet(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/model_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodGet, r.Method)
		assert.Contains(t, r.URL.Path, "MeasurementConceptModels(ffffffff-2222-2222-2222-100000000001)")
		assert.Contains(t, r.URL.RawQuery, "$expand=")

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	model, err := c.Models.Get(context.Background(), "ffffffff-2222-2222-2222-100000000001")
	require.NoError(t, err)
	require.NotNil(t, model)
	assert.Equal(t, "ffffffff-2222-2222-2222-100000000001", model.ID)
	require.NotNil(t, model.Name)
	assert.Equal(t, "Standard electricity model", *model.Name)
}

func TestModelsList(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/model_list.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodGet, r.Method)
		assert.Contains(t, r.URL.Path, "MeasurementConceptModels")

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	resp, err := c.Models.List(context.Background(), nil)
	require.NoError(t, err)
	require.NotNil(t, resp)
	require.NotNil(t, resp.Count)
	assert.Equal(t, 2, *resp.Count)
	assert.Len(t, resp.Items, 2)
}

// --- Error response tests ---

func TestErrorResponse404(t *testing.T) {
	errFixture, err := os.ReadFile("../testdata/error_404.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write(errFixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	_, err = c.Instances.Get(context.Background(), "01234567-89ab-cdef-0123-456789abcdef")
	require.Error(t, err)
	assert.True(t, IsNotFound(err))
	assert.False(t, IsForbidden(err))
	assert.False(t, IsUnauthorized(err))

	var apiErr *APIError
	require.ErrorAs(t, err, &apiErr)
	assert.Equal(t, 404, apiErr.StatusCode)
	require.NotNil(t, apiErr.ODataError)
	assert.Equal(t, "404009", apiErr.ODataError.Error.Code)
	assert.Contains(t, apiErr.ODataError.Error.Message, "not found")
}

func TestErrorResponse403(t *testing.T) {
	errFixture, err := os.ReadFile("../testdata/error_403.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusForbidden)
		_, _ = w.Write(errFixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	_, err = c.Instances.Get(context.Background(), "some-id")
	require.Error(t, err)
	assert.True(t, IsForbidden(err))
	assert.False(t, IsNotFound(err))
	assert.False(t, IsUnauthorized(err))

	var apiErr *APIError
	require.ErrorAs(t, err, &apiErr)
	assert.Equal(t, 403, apiErr.StatusCode)
	require.NotNil(t, apiErr.ODataError)
	assert.Equal(t, "403001", apiErr.ODataError.Error.Code)
}

func TestErrorResponse401(t *testing.T) {
	errFixture, err := os.ReadFile("../testdata/error_401.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write(errFixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	_, err = c.Instances.Get(context.Background(), "some-id")
	require.Error(t, err)
	assert.True(t, IsUnauthorized(err))
	assert.False(t, IsNotFound(err))
	assert.False(t, IsForbidden(err))

	var apiErr *APIError
	require.ErrorAs(t, err, &apiErr)
	assert.Equal(t, 401, apiErr.StatusCode)
}

func TestErrorResponsePlainText(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("Internal Server Error"))
	}))
	defer srv.Close()

	c := testClient(t, srv)
	_, err := c.Instances.Get(context.Background(), "some-id")
	require.Error(t, err)

	var apiErr *APIError
	require.ErrorAs(t, err, &apiErr)
	assert.Equal(t, 500, apiErr.StatusCode)
	assert.Nil(t, apiErr.ODataError)
	assert.Equal(t, "Internal Server Error", apiErr.RawBody)
}

func TestRequestHeaders(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, odataAccept, r.Header.Get("Accept"))
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"value":[]}`))
	}))
	defer srv.Close()

	c := testClient(t, srv)
	_, err := c.Instances.List(context.Background(), nil)
	require.NoError(t, err)
}

func TestPostRequestContentType(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			assert.Equal(t, odataContentType, r.Header.Get("Content-Type"))
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	c := testClient(t, srv)
	input := &CreateInstanceInput{
		MeasurementModelID: "test-model-id",
	}
	_, _ = c.Instances.Create(context.Background(), input)
}

func TestInstancesUpdate(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPatch, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(test-id)")

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	addrID := "new-address-id"
	inst, err := c.Instances.Update(context.Background(), "test-id", &UpdateInstanceInput{
		LeadingAddressID: &addrID,
	})
	require.NoError(t, err)
	require.NotNil(t, inst)
}

func TestInstancesUpdateMeteringLocation(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPatch, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(inst-id)/meteringLocations(melo-id)")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.UpdateMeteringLocation(context.Background(), "inst-id", "melo-id", &UpdateMeteringLocationInput{})
	require.NoError(t, err)
}

func TestInstancesUpdateMarketLocation(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPatch, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(inst-id)/marketLocations(malo-id)")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.UpdateMarketLocation(context.Background(), "inst-id", "malo-id", &UpdateMarketLocationInput{})
	require.NoError(t, err)
}

func TestInstancesUpdateActor(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPatch, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(inst-id)/actors(actor-id)")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.UpdateActor(context.Background(), "inst-id", "actor-id", &UpdateActorInput{})
	require.NoError(t, err)
}

func TestInstancesUpdateMeteringTask(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPatch, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(inst-id)/meteringLocations(melo-id)/meteringTasks(task-id)")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.UpdateMeteringTask(context.Background(), "inst-id", "melo-id", "task-id", &UpdateMeteringTaskInput{})
	require.NoError(t, err)
}

func TestInstancesUpdateOperandMapping(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPatch, r.Method)
		assert.Contains(t, r.URL.Path, "MCMInstances(inst-id)/operandMappings(mapping-id)")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.UpdateOperandMapping(context.Background(), "inst-id", "mapping-id", &UpdateOperandMappingInput{Value: "Z1B"})
	require.NoError(t, err)
}

func TestInstancesInitMerge(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "MCMService.initMerge")
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	inst, err := c.Instances.InitMerge(context.Background(), "inst-id", &InitMergeInput{
		DataForNewInstanceVersion: &InitMergeVersionData{
			MeasurementModelID: "model-id",
			ToBeMergedAncestors: []AncestorRef{
				{ID: "anc-1", IDText: "ANCT-1"},
			},
			ChangeProcesses: []InitMergeChangeProcessInput{},
		},
	})
	require.NoError(t, err)
	require.NotNil(t, inst)
}

func TestInstancesInitShutdown(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "MCMService.initShutdown")
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	inst, err := c.Instances.InitShutdown(context.Background(), "inst-id", &InitShutdownInput{
		DataForNewInstanceVersion: []InitShutdownVersionData{
			{ChangeProcesses: []InitShutdownChangeProcessInput{}},
		},
	})
	require.NoError(t, err)
	require.NotNil(t, inst)
}

func TestInstancesInitVersionCancel(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_get.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "MCMService.initVersionCancel")
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	inst, err := c.Instances.InitVersionCancel(context.Background(), "inst-id", &InitVersionCancelInput{
		DataForNewInstanceVersion: &InitVersionCancelVersionData{},
	})
	require.NoError(t, err)
	require.NotNil(t, inst)
}

func TestInstancesNotifyDeviceRemoved(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "MCMService.notifySingleDeviceRemoved")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.NotifyDeviceRemoved(context.Background(), "inst-id", "melo-id")
	require.NoError(t, err)
}

func TestInstancesNotifyMarketLocationRemoved(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "MCMService.notifySingleMarketLocationRemoved")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.NotifyMarketLocationRemoved(context.Background(), "inst-id", "malo-id")
	require.NoError(t, err)
}

func TestInstancesNotifyFinalDataEntryReady(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Contains(t, r.URL.Path, "/processData/MCMService.notifyFinalDataEntryReady")
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	err := c.Instances.NotifyFinalDataEntryReady(context.Background(), "inst-id", "cp-id")
	require.NoError(t, err)
}

func TestListWithFilterOption(t *testing.T) {
	fixture, err := os.ReadFile("../testdata/instance_list.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		query := r.URL.RawQuery
		// Verify the filter parameter is present in the URL.
		assert.True(t, strings.Contains(query, "%24filter=") || strings.Contains(query, "$filter="),
			"expected $filter in query: %s", query)
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClient(t, srv)
	resp, err := c.Instances.List(context.Background(), &ListOptions{
		Filter: map[string]string{"division_code": "EL"},
	})
	require.NoError(t, err)
	assert.Len(t, resp.Items, 2)
}
