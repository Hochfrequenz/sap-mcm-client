package mcm

import (
	"errors"
	"fmt"
)

// APIError represents an error returned by the SAP MCM API.
type APIError struct {
	// StatusCode is the HTTP status code of the response.
	StatusCode int
	// ODataError is the parsed OData error body, if available.
	ODataError *ODataErrorBody
	// RawBody is the raw response body as a string.
	RawBody string
}

// ODataErrorBody is the JSON error body returned by OData endpoints.
type ODataErrorBody struct {
	Error ODataErrorDetail `json:"error"`
}

// ODataErrorDetail contains the error code and message.
type ODataErrorDetail struct {
	Code    string `json:"code"`
	Message string `json:"message"`
}

// Error implements the error interface.
func (e *APIError) Error() string {
	if e.ODataError != nil {
		return fmt.Sprintf("mcm api error %d (%s): %s", e.StatusCode, e.ODataError.Error.Code, e.ODataError.Error.Message)
	}
	return fmt.Sprintf("mcm api error %d: %s", e.StatusCode, e.RawBody)
}

// IsNotFound returns true if the error is a 404 Not Found response.
func IsNotFound(err error) bool {
	var apiErr *APIError
	return errors.As(err, &apiErr) && apiErr.StatusCode == 404
}

// IsForbidden returns true if the error is a 403 Forbidden response.
func IsForbidden(err error) bool {
	var apiErr *APIError
	return errors.As(err, &apiErr) && apiErr.StatusCode == 403
}

// IsUnauthorized returns true if the error is a 401 Unauthorized response.
func IsUnauthorized(err error) bool {
	var apiErr *APIError
	return errors.As(err, &apiErr) && apiErr.StatusCode == 401
}
