package mcm

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// testClientWithTimeSeries creates a Client wired up with a TimeSeriesService
// and a MigrationService pointing to the given httptest.Server. It bypasses
// authentication by using the server's built-in HTTP client.
func testClientWithTimeSeries(t *testing.T, srv *httptest.Server) *Client {
	t.Helper()
	c := &Client{
		baseURL:    srv.URL + basePath,
		rawBaseURL: srv.URL,
		httpClient: srv.Client(),
	}
	c.Instances = &InstanceService{client: c}
	c.Classes = &ClassService{client: c}
	c.Models = &ModelService{client: c}
	c.TimeSeries = &TimeSeriesService{client: c}
	c.Migration = &MigrationService{client: c}
	return c
}

// ---------------------------------------------------------------------------
// Read endpoints — URL / query-string construction
// ---------------------------------------------------------------------------

const (
	tsID    = "123e4567-e89b-12d3-a456-426614174000"
	tsExtID = "1+1-1:1.29.0"
)

// tsReadTest captures the pieces we check for every read endpoint:
//   - the exact function name appended after /odata/v4/api/v1/TimeSeries/
//   - the single-quote-escaped identifier and (optional) fromDate/toDate values
func runTSReadTest(
	t *testing.T,
	wantFunction string,
	wantQueryContains []string,
	callFn func(c *Client) error,
) {
	t.Helper()
	fixture, err := os.ReadFile("../testdata/timeseries_data.json")
	require.NoError(t, err)

	var gotPath string
	var gotRawQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotPath = r.URL.Path
		gotRawQuery = r.URL.RawQuery
		assert.Equal(t, http.MethodGet, r.Method)
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(fixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	require.NoError(t, callFn(c))

	assert.Equal(t, "/odata/v4/api/v1/TimeSeries/"+wantFunction, gotPath)
	decodedQuery, err := url.QueryUnescape(gotRawQuery)
	require.NoError(t, err)
	for _, want := range wantQueryContains {
		assert.Contains(t, decodedQuery, want, "query %q missing %q", decodedQuery, want)
	}
}

func TestTimeSeriesGetByTimeSeriesIDBase(t *testing.T) {
	runTSReadTest(t,
		"getTimeSeriesDataByTimeSeriesID",
		[]string{"timeSeriesID='" + tsID + "'"},
		func(c *Client) error {
			points, err := c.TimeSeries.GetByTimeSeriesID(context.Background(), tsID, nil)
			require.NoError(t, err)
			require.Len(t, points, 4)
			return nil
		},
	)
}

func TestTimeSeriesGetByTimeSeriesIDSince(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataByTimeSeriesIDSince",
		[]string{"timeSeriesID='" + tsID + "'", "fromDate='2025-02-01'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetByTimeSeriesID(
				context.Background(), tsID, &TimeSeriesReadOptions{FromDate: &from},
			)
			return err
		},
	)
}

func TestTimeSeriesGetByTimeSeriesIDInPeriod(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	to := time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataByTimeSeriesIDInPeriod",
		[]string{
			"timeSeriesID='" + tsID + "'",
			"fromDate='2025-02-01'",
			"toDate='2025-02-28'",
		},
		func(c *Client) error {
			_, err := c.TimeSeries.GetByTimeSeriesID(
				context.Background(), tsID,
				&TimeSeriesReadOptions{FromDate: &from, ToDate: &to},
			)
			return err
		},
	)
}

func TestTimeSeriesGetByExternalIDBase(t *testing.T) {
	runTSReadTest(t,
		"getTimeSeriesDataByExternalID",
		[]string{"externalID='" + tsExtID + "'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetByExternalID(context.Background(), tsExtID, nil)
			return err
		},
	)
}

func TestTimeSeriesGetByExternalIDSince(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataByExternalIDSince",
		[]string{"externalID='" + tsExtID + "'", "fromDate='2025-02-01'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetByExternalID(
				context.Background(), tsExtID, &TimeSeriesReadOptions{FromDate: &from},
			)
			return err
		},
	)
}

func TestTimeSeriesGetByExternalIDInPeriod(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	to := time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataByExternalIDInPeriod",
		[]string{
			"externalID='" + tsExtID + "'",
			"fromDate='2025-02-01'",
			"toDate='2025-02-28'",
		},
		func(c *Client) error {
			_, err := c.TimeSeries.GetByExternalID(
				context.Background(), tsExtID,
				&TimeSeriesReadOptions{FromDate: &from, ToDate: &to},
			)
			return err
		},
	)
}

func TestTimeSeriesGetHistoryByTimeSeriesIDBase(t *testing.T) {
	runTSReadTest(t,
		"getTimeSeriesDataHistoryByTimeSeriesID",
		[]string{"timeSeriesID='" + tsID + "'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetHistoryByTimeSeriesID(context.Background(), tsID, nil)
			return err
		},
	)
}

func TestTimeSeriesGetHistoryByTimeSeriesIDSince(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataHistoryByTimeSeriesIDSince",
		[]string{"timeSeriesID='" + tsID + "'", "fromDate='2025-02-01'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetHistoryByTimeSeriesID(
				context.Background(), tsID, &TimeSeriesReadOptions{FromDate: &from},
			)
			return err
		},
	)
}

func TestTimeSeriesGetHistoryByTimeSeriesIDInPeriod(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	to := time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataHistoryByTimeSeriesIDInPeriod",
		[]string{"timeSeriesID='" + tsID + "'", "fromDate='2025-02-01'", "toDate='2025-02-28'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetHistoryByTimeSeriesID(
				context.Background(), tsID,
				&TimeSeriesReadOptions{FromDate: &from, ToDate: &to},
			)
			return err
		},
	)
}

func TestTimeSeriesGetHistoryByExternalIDBase(t *testing.T) {
	runTSReadTest(t,
		"getTimeSeriesDataHistoryByExternalID",
		[]string{"externalID='" + tsExtID + "'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetHistoryByExternalID(context.Background(), tsExtID, nil)
			return err
		},
	)
}

func TestTimeSeriesGetHistoryByExternalIDSince(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataHistoryByExternalIDSince",
		[]string{"externalID='" + tsExtID + "'", "fromDate='2025-02-01'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetHistoryByExternalID(
				context.Background(), tsExtID, &TimeSeriesReadOptions{FromDate: &from},
			)
			return err
		},
	)
}

func TestTimeSeriesGetHistoryByExternalIDInPeriod(t *testing.T) {
	from := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	to := time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC)
	runTSReadTest(t,
		"getTimeSeriesDataHistoryByExternalIDInPeriod",
		[]string{"externalID='" + tsExtID + "'", "fromDate='2025-02-01'", "toDate='2025-02-28'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetHistoryByExternalID(
				context.Background(), tsExtID,
				&TimeSeriesReadOptions{FromDate: &from, ToDate: &to},
			)
			return err
		},
	)
}

// ---------------------------------------------------------------------------
// Read error cases
// ---------------------------------------------------------------------------

func TestTimeSeriesReadRejectsToDateWithoutFromDate(t *testing.T) {
	// No server needed — the error is raised before any request is sent.
	srv := httptest.NewServer(http.HandlerFunc(func(_ http.ResponseWriter, _ *http.Request) {
		t.Fatal("server should not be called")
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	to := time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC)
	_, err := c.TimeSeries.GetByTimeSeriesID(
		context.Background(), tsID, &TimeSeriesReadOptions{ToDate: &to},
	)
	require.Error(t, err)
}

func TestTimeSeriesReadPagingParamsForwarded(t *testing.T) {
	top := 100
	skip := 50
	runTSReadTest(t,
		"getTimeSeriesDataByTimeSeriesID",
		[]string{"$top=100", "$skip=50", "$orderby=timestamp desc"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetByTimeSeriesID(
				context.Background(), tsID,
				&TimeSeriesReadOptions{Top: &top, Skip: &skip, OrderBy: []string{"timestamp desc"}},
			)
			return err
		},
	)
}

func TestTimeSeriesReadEscapesEmbeddedSingleQuote(t *testing.T) {
	runTSReadTest(t,
		"getTimeSeriesDataByExternalID",
		// OData V4 §5.1.1.6.1: embedded single quotes are doubled.
		[]string{"externalID='a''b'"},
		func(c *Client) error {
			_, err := c.TimeSeries.GetByExternalID(context.Background(), "a'b", nil)
			return err
		},
	)
}

// ---------------------------------------------------------------------------
// Upload
// ---------------------------------------------------------------------------

func TestTimeSeriesUploadWithoutUploadID(t *testing.T) {
	var gotMethod, gotPath string
	var gotQuery string
	var gotContentType string
	var gotFileContent string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		gotPath = r.URL.Path
		gotQuery = r.URL.RawQuery
		gotContentType = r.Header.Get("Content-Type")

		require.NoError(t, r.ParseMultipartForm(1<<20))
		f, _, err := r.FormFile("file")
		require.NoError(t, err)
		defer func() { _ = f.Close() }()
		buf, _ := io.ReadAll(f)
		gotFileContent = string(buf)

		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	err := c.TimeSeries.Upload(
		context.Background(),
		bytes.NewReader([]byte("ts payload")),
		"ts.csv",
		"",
	)
	require.NoError(t, err)

	assert.Equal(t, http.MethodPost, gotMethod)
	assert.Equal(t, "/api/v1/timeseries/uploadsc", gotPath)
	assert.Empty(t, gotQuery)
	assert.True(t, strings.HasPrefix(gotContentType, "multipart/"))
	assert.Equal(t, "ts payload", gotFileContent)
}

func TestTimeSeriesUploadWithUploadID(t *testing.T) {
	var gotPath string
	var gotQuery string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotPath = r.URL.Path
		gotQuery = r.URL.RawQuery
		require.NoError(t, r.ParseMultipartForm(1<<20))
		_, _, err := r.FormFile("file")
		require.NoError(t, err)
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	uploadID := "aaaaaaaa-bbbb-cccc-dddd-111122223333"
	err := c.TimeSeries.Upload(
		context.Background(),
		bytes.NewReader([]byte("ts payload")),
		"ts.csv",
		uploadID,
	)
	require.NoError(t, err)

	assert.Equal(t, "/api/v1/timeseries/upload", gotPath)
	assert.Contains(t, gotQuery, "uploadID="+uploadID)
}

func TestTimeSeriesUploadBuildsProperMultipart(t *testing.T) {
	// Extra assurance that the body is a well-formed multipart payload
	// that server code can actually decode (covered above, but isolated here).
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		mr, err := multipartReader(r)
		require.NoError(t, err)
		part, err := mr.NextPart()
		require.NoError(t, err)
		assert.Equal(t, "file", part.FormName())
		assert.Equal(t, "ts.csv", part.FileName())
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	require.NoError(t, c.TimeSeries.Upload(
		context.Background(),
		bytes.NewReader([]byte("hello")),
		"ts.csv",
		"",
	))
}

// multipartReader extracts a multipart.Reader from a request, handling the
// content-type boundary parsing manually.
func multipartReader(r *http.Request) (*multipart.Reader, error) {
	return r.MultipartReader()
}

// ---------------------------------------------------------------------------
// Delete
// ---------------------------------------------------------------------------

func TestTimeSeriesDeleteByTimeSeriesID(t *testing.T) {
	var gotMethod, gotPath string
	var gotQuery string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		gotPath = r.URL.Path
		gotQuery = r.URL.RawQuery
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	start := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	end := time.Date(2026, 1, 31, 0, 0, 0, 0, time.UTC)
	require.NoError(t, c.TimeSeries.DeleteByTimeSeriesID(context.Background(), tsID, start, end))

	assert.Equal(t, http.MethodDelete, gotMethod)
	assert.Equal(t, "/api/v1/timeseries/delete/"+tsID, gotPath)
	decoded, err := url.QueryUnescape(gotQuery)
	require.NoError(t, err)
	assert.Contains(t, decoded, "startTime=")
	assert.Contains(t, decoded, "endTime=")
}

func TestTimeSeriesDeleteByExternalID(t *testing.T) {
	var gotPath string

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotPath = r.URL.Path
		w.WriteHeader(http.StatusNoContent)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	start := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	end := time.Date(2026, 1, 31, 0, 0, 0, 0, time.UTC)
	require.NoError(t, c.TimeSeries.DeleteByExternalID(context.Background(), tsExtID, start, end))

	assert.Equal(t, "/api/v1/timeseries/delete/externalId/"+tsExtID, gotPath)
}

func TestTimeSeriesDeleteBulk(t *testing.T) {
	var gotMethod, gotPath string
	var gotBody []byte

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		gotPath = r.URL.Path
		var err error
		gotBody, err = io.ReadAll(r.Body)
		require.NoError(t, err)
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	req := &DeleteTimeSeriesRequest{
		UUIDs:       []string{tsID},
		ExternalIDs: []string{tsExtID},
		StartTime:   time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
		EndTime:     time.Date(2026, 1, 31, 0, 0, 0, 0, time.UTC),
	}
	require.NoError(t, c.TimeSeries.DeleteBulk(context.Background(), req))

	assert.Equal(t, http.MethodPost, gotMethod)
	assert.Equal(t, "/api/v1/timeseries/delete/bulk", gotPath)

	var body map[string]any
	require.NoError(t, json.Unmarshal(gotBody, &body))
	assert.Contains(t, body, "uuids")
	assert.Contains(t, body, "externalIds")
	assert.Contains(t, body, "startTime")
	assert.Contains(t, body, "endTime")
}

func TestTimeSeriesDeleteBulkRejectsEmptyRequest(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(_ http.ResponseWriter, _ *http.Request) {
		t.Fatal("server should not be called")
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	// No uuids or externalIds → rejected client-side.
	req := &DeleteTimeSeriesRequest{
		StartTime: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
		EndTime:   time.Date(2026, 1, 31, 0, 0, 0, 0, time.UTC),
	}
	err := c.TimeSeries.DeleteBulk(context.Background(), req)
	require.Error(t, err)
}

func TestTimeSeriesDeleteBulkRejectsNilRequest(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(_ http.ResponseWriter, _ *http.Request) {
		t.Fatal("server should not be called")
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	err := c.TimeSeries.DeleteBulk(context.Background(), nil)
	require.Error(t, err)
}

// ---------------------------------------------------------------------------
// Error propagation for read endpoints
// ---------------------------------------------------------------------------

func TestTimeSeriesReadPropagates404(t *testing.T) {
	errFixture, err := os.ReadFile("../testdata/error_404.json")
	require.NoError(t, err)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write(errFixture)
	}))
	defer srv.Close()

	c := testClientWithTimeSeries(t, srv)
	_, err = c.TimeSeries.GetByTimeSeriesID(context.Background(), tsID, nil)
	require.Error(t, err)
	assert.True(t, IsNotFound(err))
}
