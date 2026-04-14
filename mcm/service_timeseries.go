package mcm

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"path"
	"strconv"
	"strings"
	"time"
)

// TimeSeriesService handles communication with the Time Series endpoints
// of the SAP Cloud for Utilities Foundation service. Unlike the MCM
// services, its endpoints live under two separate path prefixes:
// the OData V4 read functions at /odata/v4/api/v1/TimeSeries and the
// REST-style upload/delete endpoints at /api/v1/timeseries.
type TimeSeriesService struct {
	client *Client
}

// timeSeriesDataDateFormat is the ISO date format required by the
// OData functions (YYYY-MM-DD).
const timeSeriesDataDateFormat = "2006-01-02"

// quoteODataLiteral wraps value in single quotes, doubling any
// embedded single quotes, per the OData V4 string literal rule.
func quoteODataLiteral(value string) string {
	return "'" + strings.ReplaceAll(value, "'", "''") + "'"
}

// applyPaging writes Top, Skip, and OrderBy query parameters into v.
func applyPaging(v url.Values, opts *TimeSeriesReadOptions) {
	if opts == nil {
		return
	}
	if opts.Top != nil {
		v.Set("$top", strconv.Itoa(*opts.Top))
	}
	if opts.Skip != nil {
		v.Set("$skip", strconv.Itoa(*opts.Skip))
	}
	if len(opts.OrderBy) > 0 {
		v.Set("$orderby", strings.Join(opts.OrderBy, ","))
	}
}

// dateSuffix returns the endpoint suffix ("", "Since", or "InPeriod")
// for the given date range and writes the corresponding query
// parameters into v. It errors if ToDate is set without FromDate.
func dateSuffix(v url.Values, opts *TimeSeriesReadOptions) (string, error) {
	if opts == nil || opts.FromDate == nil {
		if opts != nil && opts.ToDate != nil {
			return "", errors.New("timeseries: ToDate requires FromDate")
		}
		return "", nil
	}
	v.Set("fromDate", quoteODataLiteral(opts.FromDate.Format(timeSeriesDataDateFormat)))
	if opts.ToDate != nil {
		v.Set("toDate", quoteODataLiteral(opts.ToDate.Format(timeSeriesDataDateFormat)))
		return "InPeriod", nil
	}
	return "Since", nil
}

// odataURL builds a full URL for a Time Series OData read function.
func (s *TimeSeriesService) odataURL(function string, v url.Values) string {
	u := s.client.rawBaseURL + timeSeriesODataBasePath + "/" + function
	if encoded := v.Encode(); encoded != "" {
		u += "?" + encoded
	}
	return u
}

// restURL builds a full URL for a Time Series REST endpoint.
func (s *TimeSeriesService) restURL(suffix string) string {
	return s.client.rawBaseURL + timeSeriesRESTBasePath + "/" + strings.TrimLeft(suffix, "/")
}

// timeSeriesEnvelope matches the OData V4 collection response wrapper
// returned by the Time Series read functions.
type timeSeriesEnvelope struct {
	Value []TimeSeriesDataPoint `json:"value"`
}

// getPoints issues a GET against the given OData function and parses
// the response envelope into a slice of data points.
func (s *TimeSeriesService) getPoints(ctx context.Context, function string, v url.Values) ([]TimeSeriesDataPoint, error) {
	req, err := s.client.newAbsoluteRequest(ctx, http.MethodGet, s.odataURL(function, v), nil)
	if err != nil {
		return nil, err
	}
	body, err := s.client.doRaw(req)
	if err != nil {
		return nil, err
	}
	if len(body) == 0 {
		return nil, nil
	}
	// The spec describes the body as a top-level array, but OData V4
	// wraps collections in {"value": [...]} — accept both.
	trimmed := bytes.TrimSpace(body)
	if len(trimmed) > 0 && trimmed[0] == '[' {
		var points []TimeSeriesDataPoint
		if err := json.Unmarshal(body, &points); err != nil {
			return nil, fmt.Errorf("decoding timeseries collection: %w", err)
		}
		return points, nil
	}
	var env timeSeriesEnvelope
	if err := json.Unmarshal(body, &env); err != nil {
		return nil, fmt.Errorf("decoding timeseries collection: %w", err)
	}
	return env.Value, nil
}

// GetByTimeSeriesID retrieves current time series data points for the
// time series identified by id (a UUID). Pass nil for opts to fetch the
// full current data set.
//
// Dispatches to one of:
//   - getTimeSeriesDataByTimeSeriesID
//   - getTimeSeriesDataByTimeSeriesIDSince (when opts.FromDate is set)
//   - getTimeSeriesDataByTimeSeriesIDInPeriod (when opts.FromDate and opts.ToDate are set)
func (s *TimeSeriesService) GetByTimeSeriesID(ctx context.Context, id string, opts *TimeSeriesReadOptions) ([]TimeSeriesDataPoint, error) {
	v := url.Values{}
	v.Set("timeSeriesID", quoteODataLiteral(id))
	suffix, err := dateSuffix(v, opts)
	if err != nil {
		return nil, err
	}
	applyPaging(v, opts)
	return s.getPoints(ctx, "getTimeSeriesDataByTimeSeriesID"+suffix, v)
}

// GetByExternalID retrieves current time series data points for the
// time series identified by its external ID. Pass nil for opts to
// fetch the full current data set.
//
// Dispatches to one of:
//   - getTimeSeriesDataByExternalID
//   - getTimeSeriesDataByExternalIDSince
//   - getTimeSeriesDataByExternalIDInPeriod
func (s *TimeSeriesService) GetByExternalID(ctx context.Context, externalID string, opts *TimeSeriesReadOptions) ([]TimeSeriesDataPoint, error) {
	v := url.Values{}
	v.Set("externalID", quoteODataLiteral(externalID))
	suffix, err := dateSuffix(v, opts)
	if err != nil {
		return nil, err
	}
	applyPaging(v, opts)
	return s.getPoints(ctx, "getTimeSeriesDataByExternalID"+suffix, v)
}

// GetHistoryByTimeSeriesID retrieves historical time series data points
// for the time series identified by id (a UUID). Pass nil for opts to
// fetch the full history.
//
// Dispatches to one of:
//   - getTimeSeriesDataHistoryByTimeSeriesID
//   - getTimeSeriesDataHistoryByTimeSeriesIDSince
//   - getTimeSeriesDataHistoryByTimeSeriesIDInPeriod
func (s *TimeSeriesService) GetHistoryByTimeSeriesID(ctx context.Context, id string, opts *TimeSeriesReadOptions) ([]TimeSeriesDataPoint, error) {
	v := url.Values{}
	v.Set("timeSeriesID", quoteODataLiteral(id))
	suffix, err := dateSuffix(v, opts)
	if err != nil {
		return nil, err
	}
	applyPaging(v, opts)
	return s.getPoints(ctx, "getTimeSeriesDataHistoryByTimeSeriesID"+suffix, v)
}

// GetHistoryByExternalID retrieves historical time series data points
// for the time series identified by its external ID. Pass nil for opts
// to fetch the full history.
//
// Dispatches to one of:
//   - getTimeSeriesDataHistoryByExternalID
//   - getTimeSeriesDataHistoryByExternalIDSince
//   - getTimeSeriesDataHistoryByExternalIDInPeriod
func (s *TimeSeriesService) GetHistoryByExternalID(ctx context.Context, externalID string, opts *TimeSeriesReadOptions) ([]TimeSeriesDataPoint, error) {
	v := url.Values{}
	v.Set("externalID", quoteODataLiteral(externalID))
	suffix, err := dateSuffix(v, opts)
	if err != nil {
		return nil, err
	}
	applyPaging(v, opts)
	return s.getPoints(ctx, "getTimeSeriesDataHistoryByExternalID"+suffix, v)
}

// Upload uploads a time series file. If uploadID is non-empty, the
// explicit /upload endpoint is used with the UUID in the query string.
// Otherwise the filename-based /uploadsc endpoint is used, which
// extracts the time series identifier from the provided filename.
func (s *TimeSeriesService) Upload(ctx context.Context, file io.Reader, filename string, uploadID string) error {
	if filename == "" {
		filename = "upload.bin"
	}

	buf := &bytes.Buffer{}
	writer := multipart.NewWriter(buf)
	part, err := writer.CreateFormFile("file", path.Base(filename))
	if err != nil {
		return fmt.Errorf("timeseries upload: creating form file: %w", err)
	}
	if _, err := io.Copy(part, file); err != nil {
		return fmt.Errorf("timeseries upload: copying file body: %w", err)
	}
	if err := writer.Close(); err != nil {
		return fmt.Errorf("timeseries upload: closing multipart writer: %w", err)
	}

	var target string
	if uploadID != "" {
		q := url.Values{}
		q.Set("uploadID", uploadID)
		target = s.restURL("upload") + "?" + q.Encode()
	} else {
		target = s.restURL("uploadsc")
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, target, buf)
	if err != nil {
		return fmt.Errorf("timeseries upload: creating request: %w", err)
	}
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", writer.FormDataContentType())

	if _, err := s.client.doRaw(req); err != nil {
		return err
	}
	return nil
}

// DeleteByTimeSeriesID deletes time series data for the given UUID
// within the specified date range.
func (s *TimeSeriesService) DeleteByTimeSeriesID(ctx context.Context, id string, start, end time.Time) error {
	q := url.Values{}
	q.Set("startTime", start.UTC().Format(time.RFC3339Nano))
	q.Set("endTime", end.UTC().Format(time.RFC3339Nano))
	target := s.restURL("delete/"+id) + "?" + q.Encode()

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodDelete, target, nil)
	if err != nil {
		return err
	}
	_, err = s.client.doRaw(req)
	return err
}

// DeleteByExternalID deletes time series data for the given external
// ID within the specified date range.
func (s *TimeSeriesService) DeleteByExternalID(ctx context.Context, externalID string, start, end time.Time) error {
	q := url.Values{}
	q.Set("startTime", start.UTC().Format(time.RFC3339Nano))
	q.Set("endTime", end.UTC().Format(time.RFC3339Nano))
	target := s.restURL("delete/externalId/"+externalID) + "?" + q.Encode()

	req, err := s.client.newAbsoluteRequest(ctx, http.MethodDelete, target, nil)
	if err != nil {
		return err
	}
	_, err = s.client.doRaw(req)
	return err
}

// DeleteBulk deletes time series data in bulk by UUID and/or external
// ID lists within a date range. At least one of req.UUIDs or
// req.ExternalIDs must be non-empty; the server enforces a maximum of
// 100 identifiers per request and a maximum range of one year.
func (s *TimeSeriesService) DeleteBulk(ctx context.Context, req *DeleteTimeSeriesRequest) error {
	if req == nil {
		return errors.New("timeseries: DeleteBulk requires a non-nil request")
	}
	if len(req.UUIDs) == 0 && len(req.ExternalIDs) == 0 {
		return errors.New("timeseries: DeleteBulk requires at least one UUID or external ID")
	}

	httpReq, err := s.client.newAbsoluteRequest(ctx, http.MethodPost, s.restURL("delete/bulk"), req)
	if err != nil {
		return err
	}
	_, err = s.client.doRaw(httpReq)
	return err
}
