// OData V4 protocol abstraction for the SAP MCM API client.
//
// The $expand strings used in this file are derived from the SAP MCM
// OpenAPI specs v1.1.0 downloaded from api.sap.com.
package mcm

import (
	"encoding/json"
	"fmt"
	"net/url"
	"sort"
	"strconv"
	"strings"
)

const (
	odataAccept      = "application/json;odata.metadata=minimal;IEEE754Compatible=true"
	odataContentType = "application/json;charset=UTF-8;IEEE754Compatible=true"
)

// ListOptions holds the query parameters for paginated list operations
// against OData V4 collection endpoints.
type ListOptions struct {
	// Top limits the number of items returned ($top).
	Top *int
	// Skip skips the first N items ($skip).
	Skip *int
	// Count requests an inline count of the total items ($count=true).
	Count bool
	// OrderBy specifies the sort order ($orderby).
	OrderBy string
	// Search is a free-text search term ($search).
	Search string
	// Filter maps field names to equality filter values.
	// Keys are the OData wire-format field names; each entry produces
	// a clause of the form "key eq 'value'" joined with " and ".
	Filter map[string]string
}

// ListResponse is a generic paginated response from an OData V4 collection endpoint.
type ListResponse[T any] struct {
	// Items contains the returned entities.
	Items []T
	// Count is the total number of matching entities, present only when
	// the request included $count=true.
	Count *int
}

// queryParams converts the ListOptions into OData V4 system query parameters.
func (o *ListOptions) queryParams() url.Values {
	if o == nil {
		return nil
	}
	v := url.Values{}
	if o.Top != nil {
		v.Set("$top", strconv.Itoa(*o.Top))
	}
	if o.Skip != nil {
		v.Set("$skip", strconv.Itoa(*o.Skip))
	}
	if o.Count {
		v.Set("$count", "true")
	}
	if o.OrderBy != "" {
		v.Set("$orderby", o.OrderBy)
	}
	if o.Search != "" {
		v.Set("$search", o.Search)
	}
	if len(o.Filter) > 0 {
		// Sort keys for deterministic output.
		keys := make([]string, 0, len(o.Filter))
		for k := range o.Filter {
			keys = append(keys, k)
		}
		sort.Strings(keys)

		clauses := make([]string, 0, len(o.Filter))
		for _, k := range keys {
			clauses = append(clauses, fmt.Sprintf("%s eq '%s'", k, o.Filter[k]))
		}
		v.Set("$filter", strings.Join(clauses, " and "))
	}
	return v
}

// defaultInstanceExpand returns the full $expand string for measurement concept instances.
func defaultInstanceExpand() string {
	return "meteringLocations($expand=meteringTasks)," +
		"marketLocations($expand=calculationRules($expand=steps,usages))," +
		"operandMappings," +
		"actors," +
		"addresses," +
		"changeProcesses($expand=processData($expand=" +
		"meteringLocationsPD($expand=meteringTasksPD)," +
		"marketLocationsPD," +
		"actorsPD($expand=externalReferences))," +
		"instanceCharacteristics)," +
		"status"
}

// defaultClassExpand returns the full $expand string for measurement concept classes.
func defaultClassExpand() string {
	return "classType,division,meteringLocations,actors"
}

// defaultModelExpand returns the full $expand string for measurement concept models.
func defaultModelExpand() string {
	return "conceptType," +
		"measurementClass($expand=meteringLocations,actors)," +
		"status," +
		"division," +
		"modelOperands," +
		"marketLocations($expand=actorsMapping,calculationRules($expand=usages))," +
		"meteringLocationPurposes"
}

// odataEnvelope is the generic OData V4 collection response wrapper.
type odataEnvelope[T any] struct {
	Value []T  `json:"value"`
	Count *int `json:"@odata.count,omitempty"`
}

// parseODataCollection parses an OData V4 collection response body into a
// typed ListResponse. The body must contain a JSON object with a "value"
// array and an optional "@odata.count" integer.
func parseODataCollection[T any](body []byte) (*ListResponse[T], error) {
	var env odataEnvelope[T]
	if err := json.Unmarshal(body, &env); err != nil {
		return nil, fmt.Errorf("parsing odata collection: %w", err)
	}
	return &ListResponse[T]{
		Items: env.Value,
		Count: env.Count,
	}, nil
}
