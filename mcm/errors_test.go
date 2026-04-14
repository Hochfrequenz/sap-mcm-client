package mcm

import (
	"errors"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAPIErrorErrorWithODataError(t *testing.T) {
	apiErr := &APIError{
		StatusCode: 404,
		ODataError: &ODataErrorBody{
			Error: ODataErrorDetail{
				Code:    "404009",
				Message: "Entity 'MCMService.MCMInstances' with key(s) 'id=01234567' not found",
			},
		},
		RawBody: `{"error":{"code":"404009","message":"..."}}`,
	}
	msg := apiErr.Error()
	assert.Contains(t, msg, "404")
	assert.Contains(t, msg, "404009")
	assert.Contains(t, msg, "not found")
	assert.Contains(t, msg, "mcm api error")
}

func TestAPIErrorErrorWithoutODataError(t *testing.T) {
	apiErr := &APIError{
		StatusCode: 500,
		RawBody:    "Internal Server Error",
	}
	msg := apiErr.Error()
	assert.Contains(t, msg, "500")
	assert.Contains(t, msg, "Internal Server Error")
	assert.Contains(t, msg, "mcm api error")
}

func TestIsNotFound(t *testing.T) {
	t.Run("true for 404", func(t *testing.T) {
		err := fmt.Errorf("wrapped: %w", &APIError{StatusCode: 404})
		assert.True(t, IsNotFound(err))
	})
	t.Run("false for 403", func(t *testing.T) {
		err := fmt.Errorf("wrapped: %w", &APIError{StatusCode: 403})
		assert.False(t, IsNotFound(err))
	})
	t.Run("false for non-APIError", func(t *testing.T) {
		err := errors.New("some error")
		assert.False(t, IsNotFound(err))
	})
	t.Run("direct APIError", func(t *testing.T) {
		var err error = &APIError{StatusCode: 404}
		assert.True(t, IsNotFound(err))
	})
}

func TestIsForbidden(t *testing.T) {
	t.Run("true for 403", func(t *testing.T) {
		err := fmt.Errorf("wrapped: %w", &APIError{StatusCode: 403})
		assert.True(t, IsForbidden(err))
	})
	t.Run("false for 404", func(t *testing.T) {
		err := fmt.Errorf("wrapped: %w", &APIError{StatusCode: 404})
		assert.False(t, IsForbidden(err))
	})
	t.Run("false for non-APIError", func(t *testing.T) {
		err := errors.New("some error")
		assert.False(t, IsForbidden(err))
	})
}

func TestIsUnauthorized(t *testing.T) {
	t.Run("true for 401", func(t *testing.T) {
		err := fmt.Errorf("wrapped: %w", &APIError{StatusCode: 401})
		assert.True(t, IsUnauthorized(err))
	})
	t.Run("false for 403", func(t *testing.T) {
		err := fmt.Errorf("wrapped: %w", &APIError{StatusCode: 403})
		assert.False(t, IsUnauthorized(err))
	})
	t.Run("false for non-APIError", func(t *testing.T) {
		err := errors.New("some error")
		assert.False(t, IsUnauthorized(err))
	})
}

func TestIsNotFoundNilError(t *testing.T) {
	assert.False(t, IsNotFound(nil))
}

func TestIsForbiddenNilError(t *testing.T) {
	assert.False(t, IsForbidden(nil))
}

func TestIsUnauthorizedNilError(t *testing.T) {
	assert.False(t, IsUnauthorized(nil))
}
