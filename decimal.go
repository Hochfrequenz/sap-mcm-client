package mcm

import (
	"encoding/json"
	"fmt"
	"strings"
)

// Decimal represents a decimal number that may be serialized as either a
// JSON number or a JSON string. The SAP MCM OData API sends decimals as
// strings when the IEEE754Compatible=true header is set.
//
// Internally, the value is stored as a string to preserve the exact
// representation without floating-point rounding errors.
type Decimal struct {
	value string
	valid bool
}

// NewDecimal creates a Decimal from a string representation.
func NewDecimal(s string) Decimal {
	return Decimal{value: s, valid: true}
}

// String returns the string representation of the decimal value.
// Returns "0" for zero-value Decimals.
func (d Decimal) String() string {
	if !d.valid {
		return "0"
	}
	return d.value
}

// IsZero returns true if the Decimal is the zero value (unset).
func (d Decimal) IsZero() bool {
	return !d.valid
}

// MarshalJSON serializes the Decimal as a JSON string, which is required
// for IEEE754Compatible mode in OData V4.
func (d Decimal) MarshalJSON() ([]byte, error) {
	if !d.valid {
		return []byte("null"), nil
	}
	return json.Marshal(d.value)
}

// UnmarshalJSON deserializes the Decimal from either a JSON string
// (IEEE754Compatible mode) or a JSON number.
func (d *Decimal) UnmarshalJSON(data []byte) error {
	s := strings.TrimSpace(string(data))
	if s == "null" {
		d.valid = false
		d.value = ""
		return nil
	}
	// JSON string: "1.23456"
	if len(s) >= 2 && s[0] == '"' && s[len(s)-1] == '"' {
		d.value = s[1 : len(s)-1]
		d.valid = true
		return nil
	}
	// JSON number: 1.23456
	var n json.Number
	if err := json.Unmarshal(data, &n); err != nil {
		return fmt.Errorf("decimal: cannot unmarshal %s: %w", s, err)
	}
	d.value = n.String()
	d.valid = true
	return nil
}
