package mcm

import "time"

// TimeSeriesDataPoint represents a single time series data record returned
// by the SAP Time Series API. The spec defines two schemas —
// TimeSeriesDataExtended (current data) and TimeSeriesDataHistoryValues
// (historical data) — with identical fields; this unified type
// represents both.
type TimeSeriesDataPoint struct {
	// ID is the identifier of the time series data point record.
	ID string `json:"ID"`
	// ImportID is the identifier of the import batch that produced this data point.
	ImportID string `json:"importID"`
	// Timestamp is the point in time to which this data point applies.
	Timestamp time.Time `json:"timestamp"`
	// TimeZoneCode is the time zone code associated with the timestamp.
	TimeZoneCode string `json:"timeZoneCode"`
	// CreatedAt is the date and time at which the data point record was created.
	CreatedAt time.Time `json:"createdAt"`
	// Value is the measured or calculated value at the given timestamp.
	// It may be nil when the value is missing. The Time Series API defines
	// this field as a JSON number (Edm.Double), so it uses NumberDecimal,
	// which marshals to a number literal rather than an IEEE754 string.
	Value *NumberDecimal `json:"value,omitempty"`
	// Missing indicates whether the data point's value is missing.
	Missing bool `json:"missing"`
	// Quality is the quality indicator for the data point.
	Quality string `json:"quality"`
	// TimeSeriesID is the universally unique identifier (UUID) of the
	// time series to which this data point belongs.
	TimeSeriesID string `json:"timeSeriesID"`
	// ExternalID is the external identifier of the time series to which
	// this data point belongs.
	ExternalID string `json:"externalID"`
}

// DeleteTimeSeriesRequest is the request body for the Time Series bulk
// delete endpoint. At least one of UUIDs or ExternalIDs must be present;
// the server enforces a maximum of 100 identifiers per request and a
// maximum date range of one year between StartTime and EndTime.
type DeleteTimeSeriesRequest struct {
	// UUIDs is the list of time series UUIDs that are to be deleted.
	UUIDs []string `json:"uuids,omitempty"`
	// ExternalIDs is the list of externalIDs that are to be deleted.
	ExternalIDs []string `json:"externalIds,omitempty"`
	// StartTime is the (required) start timestamp for deletion.
	StartTime time.Time `json:"startTime"`
	// EndTime is the (required) end timestamp for deletion.
	EndTime time.Time `json:"endTime"`
}

// TimeSeriesReadOptions holds optional parameters for the OData Time
// Series read endpoints. Nil or zero-length fields are omitted from
// the request.
type TimeSeriesReadOptions struct {
	// FromDate narrows results to points on or after this date.
	// When set alone, the "Since" variant is used; when set together
	// with ToDate, the "InPeriod" variant is used.
	FromDate *time.Time
	// ToDate narrows results to points on or before this date.
	// Requires FromDate to also be set.
	ToDate *time.Time
	// Top limits the number of items returned ($top).
	Top *int
	// Skip skips the first n items ($skip).
	Skip *int
	// OrderBy specifies the sort order ($orderby). Each entry is a
	// single OData order-by clause (e.g. "timestamp desc").
	OrderBy []string
}
