package mcm

import (
	"context"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// captureHandler is a slog.Handler that records every emitted record so tests
// can assert on the structured "wide event" fields.
type captureHandler struct {
	mu      sync.Mutex
	records []slog.Record
}

func (h *captureHandler) Enabled(context.Context, slog.Level) bool { return true }

func (h *captureHandler) Handle(_ context.Context, r slog.Record) error {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.records = append(h.records, r.Clone())
	return nil
}

func (h *captureHandler) WithAttrs([]slog.Attr) slog.Handler { return h }
func (h *captureHandler) WithGroup(string) slog.Handler      { return h }

func (h *captureHandler) eventsNamed(name string) []slog.Record {
	h.mu.Lock()
	defer h.mu.Unlock()
	var out []slog.Record
	for _, r := range h.records {
		if attrsOf(r)["event"] == name {
			out = append(out, r)
		}
	}
	return out
}

// attrsOf flattens a record's attributes into a map for easy assertions.
func attrsOf(r slog.Record) map[string]any {
	m := map[string]any{}
	r.Attrs(func(a slog.Attr) bool {
		m[a.Key] = a.Value.Any()
		return true
	})
	return m
}

// loggingClient builds a Client pointing at srv with the given logger and no
// authentication (uses the test server's own client).
func loggingClient(srv *httptest.Server, logger *slog.Logger) *Client {
	c := &Client{
		baseURL:    srv.URL + basePath,
		rawBaseURL: srv.URL,
		httpClient: srv.Client(),
		logger:     logger,
	}
	c.Instances = &InstanceService{client: c}
	return c
}

func TestRequestWideEventSuccess(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"value":[]}`))
	}))
	defer srv.Close()

	capture := &captureHandler{}
	c := loggingClient(srv, slog.New(capture))

	req, err := c.newRequest(context.Background(), http.MethodGet, "/MCMInstances", nil)
	require.NoError(t, err)
	_, err = c.doRaw(req)
	require.NoError(t, err)

	events := capture.eventsNamed("mcm.request")
	require.Len(t, events, 1)
	rec := events[0]
	attrs := attrsOf(rec)

	assert.Equal(t, slog.LevelInfo, rec.Level)
	assert.Equal(t, "GET", attrs["http_method"])
	assert.Equal(t, int64(200), attrs["http_status"])
	assert.Equal(t, true, attrs["ok"])
	assert.Contains(t, attrs["url"], "/MCMInstances")
	assert.NotContains(t, attrs["url"], "?") // query is never logged
	assert.IsType(t, float64(0), attrs["duration_ms"])
	assert.Greater(t, attrs["response_bytes"], int64(0))

	requestID, ok := attrs["request_id"].(string)
	require.True(t, ok)
	assert.Len(t, requestID, 32)
}

func TestRequestWideEventRequestIDsUnique(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	capture := &captureHandler{}
	c := loggingClient(srv, slog.New(capture))

	for i := 0; i < 2; i++ {
		req, err := c.newRequest(context.Background(), http.MethodGet, "/MCMInstances", nil)
		require.NoError(t, err)
		_, err = c.doRaw(req)
		require.NoError(t, err)
	}

	events := capture.eventsNamed("mcm.request")
	require.Len(t, events, 2)
	assert.NotEqual(t, attrsOf(events[0])["request_id"], attrsOf(events[1])["request_id"])
}

func TestRequestWideEventLevelsByStatus(t *testing.T) {
	cases := []struct {
		status int
		level  slog.Level
	}{
		{http.StatusNotFound, slog.LevelWarn},
		{http.StatusServiceUnavailable, slog.LevelError},
	}
	for _, tc := range cases {
		srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
			w.WriteHeader(tc.status)
			_, _ = w.Write([]byte(`{"error":{"code":"x","message":"y"}}`))
		}))

		capture := &captureHandler{}
		c := loggingClient(srv, slog.New(capture))

		req, err := c.newRequest(context.Background(), http.MethodGet, "/MCMInstances", nil)
		require.NoError(t, err)
		_, err = c.doRaw(req)
		require.Error(t, err) // >= 400 returns an APIError

		events := capture.eventsNamed("mcm.request")
		require.Len(t, events, 1)
		assert.Equal(t, tc.level, events[0].Level)
		assert.Equal(t, int64(tc.status), attrsOf(events[0])["http_status"])
		assert.Equal(t, false, attrsOf(events[0])["ok"])
		srv.Close()
	}
}

func TestRequestWideEventTransportError(t *testing.T) {
	capture := &captureHandler{}
	// 127.0.0.1:1 reliably refuses connections.
	c := &Client{
		baseURL:    "http://127.0.0.1:1" + basePath,
		httpClient: &http.Client{},
		logger:     slog.New(capture),
	}

	req, err := c.newRequest(context.Background(), http.MethodGet, "/MCMInstances", nil)
	require.NoError(t, err)
	_, err = c.doRaw(req)
	require.Error(t, err)

	events := capture.eventsNamed("mcm.request")
	require.Len(t, events, 1)
	assert.Equal(t, slog.LevelError, events[0].Level)
	assert.Equal(t, false, attrsOf(events[0])["ok"])
	assert.NotEmpty(t, attrsOf(events[0])["error"])
}

func TestNilLoggerDoesNotPanic(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	c := loggingClient(srv, nil) // logger nil, as direct struct construction allows
	req, err := c.newRequest(context.Background(), http.MethodGet, "/MCMInstances", nil)
	require.NoError(t, err)
	_, err = c.doRaw(req)
	assert.NoError(t, err)
}

func TestNewClientDefaultsToSilentLogger(t *testing.T) {
	c := NewClient(Config{
		BaseURL: "https://example.com",
		Auth:    AuthConfig{TokenURL: "https://auth.example.com/token", ClientID: "id", ClientSecret: "sec"},
	})
	require.NotNil(t, c.logger) // a discard logger, never nil
}

func TestTokenFetchWideEventSuccess(t *testing.T) {
	srv, _ := newTestTokenServer(t, "secret-access-token", 3600)
	defer srv.Close()

	capture := &captureHandler{}
	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	}, slog.New(capture))

	_, err := ts.Token(context.Background())
	require.NoError(t, err)

	events := capture.eventsNamed("mcm.token_fetch")
	require.Len(t, events, 1)
	attrs := attrsOf(events[0])
	assert.Equal(t, slog.LevelInfo, events[0].Level)
	assert.Equal(t, true, attrs["ok"])
	assert.Equal(t, int64(3600), attrs["expires_in"])

	// Neither the access token nor the client secret may appear anywhere.
	blob := recordString(events[0])
	assert.NotContains(t, blob, "secret-access-token")
	assert.NotContains(t, blob, "test-client-secret")
}

func TestTokenFetchWideEventFailureSanitized(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("super-secret-body-leak"))
	}))
	defer srv.Close()

	capture := &captureHandler{}
	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	}, slog.New(capture))

	_, err := ts.Token(context.Background())
	require.Error(t, err)

	events := capture.eventsNamed("mcm.token_fetch")
	require.Len(t, events, 1)
	assert.Equal(t, slog.LevelError, events[0].Level)
	assert.Equal(t, false, attrsOf(events[0])["ok"])
	// The token-endpoint response body must never reach the log.
	assert.NotContains(t, recordString(events[0]), "super-secret-body-leak")
}

// recordString renders a record's message and all attribute keys/values into a
// single string for leakage assertions.
func recordString(r slog.Record) string {
	var b strings.Builder
	b.WriteString(r.Message)
	r.Attrs(func(a slog.Attr) bool {
		b.WriteString(" ")
		b.WriteString(a.Key)
		b.WriteString("=")
		b.WriteString(a.Value.String())
		return true
	})
	return b.String()
}
