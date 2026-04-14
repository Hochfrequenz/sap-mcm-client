package mcm

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

const basePath = "/odata/v4/api/mcm/v1"

// Config holds the configuration for creating a new MCM API Client.
type Config struct {
	// BaseURL is the SAP MCM service base URL (e.g. "https://tenant.cfapps.eu10.hana.ondemand.com").
	BaseURL string
	// Auth contains the OAuth2 client credentials for authentication.
	Auth AuthConfig
	// Timeout is the HTTP client timeout. Defaults to 30 seconds when zero.
	Timeout time.Duration
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

	baseURL    string
	httpClient *http.Client
}

// NewClient creates a new MCM API client with the given configuration.
// The returned client automatically handles OAuth2 token acquisition and
// renewal using the provided credentials.
func NewClient(cfg Config) *Client {
	timeout := cfg.Timeout
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	c := &Client{
		baseURL:    strings.TrimRight(cfg.BaseURL, "/") + basePath,
		httpClient: newAuthenticatedClient(cfg.Auth, timeout),
	}

	c.Instances = &InstanceService{client: c}
	c.Classes = &ClassService{client: c}
	c.Models = &ModelService{client: c}

	return c
}

// newRequest creates an HTTP request with the standard OData headers set.
// If body is non-nil it is marshaled to JSON and set as the request body.
func (c *Client) newRequest(ctx context.Context, method, path string, body any) (*http.Request, error) {
	url := c.baseURL + "/" + strings.TrimLeft(path, "/")

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
func (c *Client) doRaw(req *http.Request) ([]byte, error) {
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("executing request: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("reading response body: %w", err)
	}

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
