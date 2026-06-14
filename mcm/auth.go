// OAuth2 Client Credentials authentication for the SAP MCM API client.
package mcm

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

// AuthConfig holds the OAuth2 client credentials configuration needed to
// authenticate against the SAP Cloud for Utilities token endpoint.
type AuthConfig struct {
	// TokenURL is the OAuth2 token endpoint URL.
	TokenURL string
	// ClientID is the OAuth2 client identifier.
	ClientID string
	// ClientSecret is the OAuth2 client secret.
	ClientSecret string
}

// tokenSource fetches and caches OAuth2 bearer tokens using the client
// credentials grant. It is safe for concurrent use.
type tokenSource struct {
	cfg       AuthConfig
	token     string
	expiresAt time.Time
	mu        sync.Mutex
	client    *http.Client // used exclusively for token requests
	logger    *slog.Logger
}

// tokenResponse is the JSON body returned by the OAuth2 token endpoint.
type tokenResponse struct {
	AccessToken string `json:"access_token"`
	ExpiresIn   int    `json:"expires_in"`
	TokenType   string `json:"token_type"`
}

// newTokenSource creates a tokenSource for the given AuthConfig. The logger
// receives a structured token-fetch event; it must be non-nil.
func newTokenSource(cfg AuthConfig, logger *slog.Logger) *tokenSource {
	return &tokenSource{
		cfg: cfg,
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
		logger: logger,
	}
}

// Token returns a valid bearer token, refreshing it if the cached token
// has expired or will expire within 30 seconds.
func (ts *tokenSource) Token(ctx context.Context) (string, error) {
	ts.mu.Lock()
	defer ts.mu.Unlock()

	// Return the cached token if it is still valid with a 30-second buffer.
	if ts.token != "" && time.Now().Before(ts.expiresAt.Add(-30*time.Second)) {
		return ts.token, nil
	}

	tok, err := ts.fetchToken(ctx)
	if err != nil {
		return "", err
	}

	ts.token = tok.AccessToken
	ts.expiresAt = time.Now().Add(time.Duration(tok.ExpiresIn) * time.Second)
	return ts.token, nil
}

// fetchToken performs the OAuth2 client_credentials grant request. It emits a
// single redaction-safe "mcm.token_fetch" event (the client secret, access
// token, and response body are never logged).
func (ts *tokenSource) fetchToken(ctx context.Context) (*tokenResponse, error) {
	started := time.Now()

	data := url.Values{
		"grant_type": {"client_credentials"},
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.cfg.TokenURL, strings.NewReader(data.Encode()))
	if err != nil {
		ts.logTokenFetch(ctx, started, 0, err)
		return nil, fmt.Errorf("creating token request: %w", err)
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.SetBasicAuth(ts.cfg.ClientID, ts.cfg.ClientSecret)

	resp, err := ts.client.Do(req)
	if err != nil {
		ts.logTokenFetch(ctx, started, 0, err)
		return nil, fmt.Errorf("executing token request: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		ts.logTokenFetch(ctx, started, resp.StatusCode, err)
		return nil, fmt.Errorf("reading token response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		// Log only the status — never the response body, which could echo
		// request details back.
		ts.logTokenFetch(ctx, started, resp.StatusCode, fmt.Errorf("status %d", resp.StatusCode))
		return nil, fmt.Errorf("token request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var tok tokenResponse
	if err := json.Unmarshal(body, &tok); err != nil {
		ts.logTokenFetch(ctx, started, resp.StatusCode, fmt.Errorf("malformed token response"))
		return nil, fmt.Errorf("parsing token response: %w", err)
	}

	if tok.AccessToken == "" {
		ts.logTokenFetch(ctx, started, resp.StatusCode, fmt.Errorf("token response missing access_token"))
		return nil, fmt.Errorf("token response missing access_token")
	}

	ts.logTokenFetchOK(ctx, started, tok.ExpiresIn)
	return &tok, nil
}

// logTokenFetch emits a failed token-fetch event. The error is sanitized by
// the caller so that neither credentials nor the response body are logged.
func (ts *tokenSource) logTokenFetch(ctx context.Context, started time.Time, status int, err error) {
	if ts.logger == nil {
		return
	}
	attrs := []slog.Attr{
		slog.String("event", "mcm.token_fetch"),
		slog.String("token_url", ts.cfg.TokenURL),
		slog.Float64("duration_ms", elapsedMS(started)),
		slog.Bool("ok", false),
		slog.String("error", err.Error()),
	}
	if status != 0 {
		attrs = append(attrs, slog.Int("http_status", status))
	}
	ts.logger.LogAttrs(ctx, slog.LevelError, "mcm token fetch failed", attrs...)
}

// logTokenFetchOK emits a successful token-fetch event. The access token is
// never logged; only its lifetime (expires_in) is recorded.
func (ts *tokenSource) logTokenFetchOK(ctx context.Context, started time.Time, expiresIn int) {
	if ts.logger == nil {
		return
	}
	ts.logger.LogAttrs(ctx, slog.LevelInfo, "mcm token fetched",
		slog.String("event", "mcm.token_fetch"),
		slog.String("token_url", ts.cfg.TokenURL),
		slog.Float64("duration_ms", elapsedMS(started)),
		slog.Bool("ok", true),
		slog.Int("expires_in", expiresIn),
	)
}

// authTransport is an http.RoundTripper that injects a Bearer token into
// every outgoing request.
type authTransport struct {
	source *tokenSource
	base   http.RoundTripper
}

// RoundTrip adds the Authorization header and delegates to the base transport.
func (t *authTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	token, err := t.source.Token(req.Context())
	if err != nil {
		return nil, fmt.Errorf("obtaining auth token: %w", err)
	}

	// Clone the request to avoid mutating the caller's request.
	r := req.Clone(req.Context())
	r.Header.Set("Authorization", "Bearer "+token)
	return t.base.RoundTrip(r)
}

// newAuthenticatedClient creates an http.Client that automatically adds
// Bearer token authentication to every request. The token is obtained via
// the OAuth2 client credentials grant and cached until shortly before expiry.
func newAuthenticatedClient(cfg AuthConfig, timeout time.Duration, logger *slog.Logger) *http.Client {
	ts := newTokenSource(cfg, logger)
	return &http.Client{
		Timeout: timeout,
		Transport: &authTransport{
			source: ts,
			base:   http.DefaultTransport,
		},
	}
}
