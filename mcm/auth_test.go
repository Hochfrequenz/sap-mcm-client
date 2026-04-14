package mcm

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func newTestTokenServer(t *testing.T, token string, expiresIn int) (*httptest.Server, *atomic.Int32) {
	t.Helper()
	var callCount atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		callCount.Add(1)

		// Validate the request.
		assert.Equal(t, http.MethodPost, r.Method)
		assert.Equal(t, "application/x-www-form-urlencoded", r.Header.Get("Content-Type"))

		user, pass, ok := r.BasicAuth()
		assert.True(t, ok, "expected basic auth")
		assert.Equal(t, "test-client-id", user)
		assert.Equal(t, "test-client-secret", pass)

		err := r.ParseForm()
		require.NoError(t, err)
		assert.Equal(t, "client_credentials", r.FormValue("grant_type"))

		resp := tokenResponse{
			AccessToken: token,
			ExpiresIn:   expiresIn,
			TokenType:   "bearer",
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(resp)
	}))
	return srv, &callCount
}

func TestTokenSourceFetchToken(t *testing.T) {
	srv, callCount := newTestTokenServer(t, "my-access-token", 3600)
	defer srv.Close()

	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	tok, err := ts.Token(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "my-access-token", tok)
	assert.Equal(t, int32(1), callCount.Load())
}

func TestTokenSourceCaching(t *testing.T) {
	srv, callCount := newTestTokenServer(t, "cached-token", 3600)
	defer srv.Close()

	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	// First call fetches the token.
	tok1, err := ts.Token(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "cached-token", tok1)
	assert.Equal(t, int32(1), callCount.Load())

	// Second call returns the cached token without hitting the server.
	tok2, err := ts.Token(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "cached-token", tok2)
	assert.Equal(t, int32(1), callCount.Load())
}

func TestTokenSourceRefreshOnExpiry(t *testing.T) {
	var callCount atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		count := callCount.Add(1)
		token := "token-v1"
		if count > 1 {
			token = "token-v2"
		}
		resp := tokenResponse{
			AccessToken: token,
			ExpiresIn:   3600,
			TokenType:   "bearer",
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(resp)
	}))
	defer srv.Close()

	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	// First call.
	tok1, err := ts.Token(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "token-v1", tok1)
	assert.Equal(t, int32(1), callCount.Load())

	// Simulate token expiry by manipulating expiresAt.
	ts.mu.Lock()
	ts.expiresAt = time.Now().Add(-1 * time.Minute)
	ts.mu.Unlock()

	// Second call should refresh.
	tok2, err := ts.Token(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "token-v2", tok2)
	assert.Equal(t, int32(2), callCount.Load())
}

func TestTokenSourceRefreshWhenNearExpiry(t *testing.T) {
	var callCount atomic.Int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		callCount.Add(1)
		resp := tokenResponse{
			AccessToken: "refreshed-token",
			ExpiresIn:   3600,
			TokenType:   "bearer",
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(resp)
	}))
	defer srv.Close()

	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	// First call.
	_, err := ts.Token(context.Background())
	require.NoError(t, err)

	// Set expiry within the 30-second buffer.
	ts.mu.Lock()
	ts.expiresAt = time.Now().Add(20 * time.Second)
	ts.mu.Unlock()

	// Should refresh because we're within the 30-second buffer.
	tok, err := ts.Token(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "refreshed-token", tok)
	assert.Equal(t, int32(2), callCount.Load())
}

func TestTokenSourceErrorOnFetchFailure(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("internal error"))
	}))
	defer srv.Close()

	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	_, err := ts.Token(context.Background())
	require.Error(t, err)
	assert.Contains(t, err.Error(), "500")
}

func TestTokenSourceErrorOnEmptyAccessToken(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := tokenResponse{
			AccessToken: "",
			ExpiresIn:   3600,
			TokenType:   "bearer",
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(resp)
	}))
	defer srv.Close()

	ts := newTokenSource(AuthConfig{
		TokenURL:     srv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	_, err := ts.Token(context.Background())
	require.Error(t, err)
	assert.Contains(t, err.Error(), "missing access_token")
}

func TestTokenSourceErrorOnInvalidURL(t *testing.T) {
	ts := newTokenSource(AuthConfig{
		TokenURL:     "http://127.0.0.1:1/invalid",
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	_, err := ts.Token(context.Background())
	require.Error(t, err)
}

func TestAuthTransportAddsBearer(t *testing.T) {
	tokenSrv, _ := newTestTokenServer(t, "bearer-test-token", 3600)
	defer tokenSrv.Close()

	var receivedAuth string
	apiSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		receivedAuth = r.Header.Get("Authorization")
		w.WriteHeader(http.StatusOK)
	}))
	defer apiSrv.Close()

	ts := newTokenSource(AuthConfig{
		TokenURL:     tokenSrv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	})

	transport := &authTransport{
		source: ts,
		base:   http.DefaultTransport,
	}

	client := &http.Client{Transport: transport}
	resp, err := client.Get(apiSrv.URL)
	require.NoError(t, err)
	defer func() { _ = resp.Body.Close() }()

	assert.Equal(t, "Bearer bearer-test-token", receivedAuth)
}

func TestNewAuthenticatedClient(t *testing.T) {
	tokenSrv, _ := newTestTokenServer(t, "full-flow-token", 3600)
	defer tokenSrv.Close()

	client := newAuthenticatedClient(AuthConfig{
		TokenURL:     tokenSrv.URL,
		ClientID:     "test-client-id",
		ClientSecret: "test-client-secret",
	}, 10*time.Second)

	require.NotNil(t, client)
	assert.Equal(t, 10*time.Second, client.Timeout)
}
