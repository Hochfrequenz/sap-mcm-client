package mcm

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"math"
	"net/http"
	"net/url"
	"strings"
	"time"
)

const (
	basePath                = "/odata/v4/api/mcm/v1"
	migrationBasePath       = "/odata/v4/api/migrate/v1"
	timeSeriesODataBasePath = "/odata/v4/api/v1/TimeSeries"
	timeSeriesRESTBasePath  = "/api/v1/timeseries"

	// Event names for the structured "wide event" log records.
	eventRequest    = "mcm.request"
	eventTokenFetch = "mcm.token_fetch"
)

// Config holds the configuration for creating a new MCM API Client.
type Config struct {
	// BaseURL is the SAP MCM service base URL (e.g. "https://tenant.cfapps.eu10.hana.ondemand.com").
	BaseURL string
	// Auth contains the OAuth2 client credentials for authentication.
	Auth AuthConfig
	// Timeout is the HTTP client timeout. Defaults to 30 seconds when zero.
	Timeout time.Duration
	// Logger receives one structured "wide event" per outbound request (and
	// per OAuth2 token fetch). When nil, logging is disabled. Credentials are
	// never logged.
	Logger *slog.Logger
}

// Client provides access to the SAP MCM APIs.
//
// Use [NewClient] to create a properly initialized client, then access
// resources through the typed service fields.
type Client struct {
	// Instances provides operations on measurement concept instances.
	Instances *InstanceService
	// Classes provides operations on measurement concept classes.
	Classes *ClassService
	// Models provides operations on measurement concept models.
	Models *ModelService
	// Migration provides access to the Measurement Concept Instance Migration API.
	Migration *MigrationService
	// TimeSeries provides operations on the SAP Time Series API.
	TimeSeries *TimeSeriesService

	baseURL    string // MCM-prefixed base URL (host + /odata/v4/api/mcm/v1).
	rawBaseURL string // Host-only base URL, used by services with non-MCM prefixes.
	httpClient *http.Client
	logger     *slog.Logger
}

// NewClient creates a new MCM API client with the given configuration.
// The returned client automatically handles OAuth2 token acquisition and
// renewal using the provided credentials.
func NewClient(cfg Config) *Client {
	timeout := cfg.Timeout
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	logger := cfg.Logger
	if logger == nil {
		// A library must not log unless the application asks it to; discard
		// everything by default (the analogue of a NullHandler).
		logger = slog.New(slog.DiscardHandler)
	}

	raw := strings.TrimRight(cfg.BaseURL, "/")
	c := &Client{
		baseURL:    raw + basePath,
		rawBaseURL: raw,
		httpClient: newAuthenticatedClient(cfg.Auth, timeout, logger),
		logger:     logger,
	}

	c.Instances = &InstanceService{client: c}
	c.Classes = &ClassService{client: c}
	c.Models = &ModelService{client: c}
	c.Migration = &MigrationService{client: c}
	c.TimeSeries = &TimeSeriesService{client: c}

	return c
}

// newRequest creates an HTTP request with the standard OData headers set.
// If body is non-nil it is marshaled to JSON and set as the request body.
func (c *Client) newRequest(ctx context.Context, method, path string, body any) (*http.Request, error) {
	url := c.baseURL + "/" + strings.TrimLeft(path, "/")
	return c.newAbsoluteRequest(ctx, method, url, body)
}

// newAbsoluteRequest creates an HTTP request at an explicit URL, setting
// the standard OData headers. Used by services whose endpoints live
// outside the MCM base path (for example, the Time Series API).
func (c *Client) newAbsoluteRequest(ctx context.Context, method, url string, body any) (*http.Request, error) {
	var bodyReader io.Reader
	if body != nil {
		buf, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("marshaling request body: %w", err)
		}
		bodyReader = bytes.NewReader(buf)
	}

	req, err := http.NewRequestWithContext(ctx, method, url, bodyReader)
	if err != nil {
		return nil, fmt.Errorf("creating request: %w", err)
	}

	req.Header.Set("Accept", odataAccept)
	if body != nil {
		req.Header.Set("Content-Type", odataContentType)
	}

	return req, nil
}

// doRaw executes the HTTP request and returns the raw response body.
// For status codes >= 400 an [APIError] is returned.
//
// Exactly one structured "wide event" is logged per call (see [Config.Logger]):
// a single canonical record carrying the method, path, status, duration and a
// high-cardinality request_id, rather than several fragmented lines. The level
// reflects the outcome (2xx info, 4xx warn, 5xx and transport errors error),
// and credentials are never logged.
func (c *Client) doRaw(req *http.Request) ([]byte, error) {
	requestID := newRequestID()
	started := time.Now()

	resp, err := c.httpClient.Do(req)
	if err != nil {
		c.logRequest(req, requestID, started, 0, 0, err)
		return nil, fmt.Errorf("executing request: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.logRequest(req, requestID, started, resp.StatusCode, 0, err)
		return nil, fmt.Errorf("reading response body: %w", err)
	}

	c.logRequest(req, requestID, started, resp.StatusCode, len(body), nil)

	if resp.StatusCode >= 400 {
		apiErr := &APIError{
			StatusCode: resp.StatusCode,
			RawBody:    string(body),
		}
		var odataErr ODataErrorBody
		if json.Unmarshal(body, &odataErr) == nil && odataErr.Error.Code != "" {
			apiErr.ODataError = &odataErr
		}
		return nil, apiErr
	}

	return body, nil
}

// do executes the HTTP request and decodes the response. If v is non-nil the
// response body is JSON-decoded into v. For status codes >= 400 an [APIError]
// is returned, optionally containing the parsed OData error body.
func (c *Client) do(req *http.Request, v any) error {
	body, err := c.doRaw(req)
	if err != nil {
		return err
	}

	if v != nil && len(body) > 0 {
		if err := json.Unmarshal(body, v); err != nil {
			return fmt.Errorf("decoding response body: %w", err)
		}
	}

	return nil
}

// logRequest emits the single structured "wide event" for one request.
// A non-nil reqErr marks a transport-level failure (no HTTP response);
// otherwise status and respBytes describe the completed response.
func (c *Client) logRequest(req *http.Request, requestID string, started time.Time, status, respBytes int, reqErr error) {
	if c.logger == nil {
		return
	}
	attrs := []slog.Attr{
		slog.String("event", eventRequest),
		slog.String("request_id", requestID),
		slog.String("http_method", req.Method),
		slog.String("url", loggedURL(req.URL)),
		slog.Float64("duration_ms", elapsedMS(started)),
	}
	ctx := req.Context()
	if reqErr != nil {
		attrs = append(attrs, slog.Bool("ok", false), slog.String("error", sanitizeError(reqErr)))
		c.logger.LogAttrs(ctx, slog.LevelError, "mcm request failed", attrs...)
		return
	}

	// Level reflects the outcome so errors always surface even when the happy
	// path is quiet: 2xx -> info, 4xx -> warn, 5xx -> error.
	level := slog.LevelInfo
	switch {
	case status >= 500:
		level = slog.LevelError
	case status >= 400:
		level = slog.LevelWarn
	}
	attrs = append(attrs,
		slog.Int("http_status", status),
		slog.Int("response_bytes", respBytes),
		slog.Bool("ok", status >= 200 && status < 300),
	)
	c.logger.LogAttrs(ctx, level, "mcm request", attrs...)
}

// newRequestID returns a 32-character hex request identifier (high
// cardinality, unique per request).
func newRequestID() string {
	var b [16]byte
	if _, err := rand.Read(b[:]); err != nil {
		// crypto/rand failure is effectively impossible; an empty id is an
		// acceptable degradation and never blocks the request.
		return ""
	}
	return hex.EncodeToString(b[:])
}

// sanitizeError renders an error for logging without leaking the request URL.
// net/http transport failures are *url.Error values whose Error() embeds the
// full URL, query string included; we log only the underlying cause so query
// parameters never reach the log (the path is logged separately via the
// "url" attribute, already query-stripped).
func sanitizeError(err error) string {
	var urlErr *url.Error
	if errors.As(err, &urlErr) && urlErr.Err != nil {
		return urlErr.Err.Error()
	}
	return err.Error()
}

// loggedURL renders a URL for logging with the query string and fragment
// stripped — query parameters are deliberately not logged.
func loggedURL(u *url.URL) string {
	if u == nil {
		return ""
	}
	cleaned := *u
	cleaned.RawQuery = ""
	cleaned.Fragment = ""
	return cleaned.String()
}

// elapsedMS returns the milliseconds elapsed since started, rounded to 3
// decimal places.
func elapsedMS(started time.Time) float64 {
	ms := float64(time.Since(started).Nanoseconds()) / 1e6
	return math.Round(ms*1000) / 1000
}
