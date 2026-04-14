package mcm

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewDecimal(t *testing.T) {
	d := NewDecimal("1.23456")
	assert.False(t, d.IsZero())
	assert.Equal(t, "1.23456", d.String())
}

func TestDecimalZeroValue(t *testing.T) {
	var d Decimal
	assert.True(t, d.IsZero())
	assert.Equal(t, "0", d.String())
}

func TestDecimalUnmarshalJSONString(t *testing.T) {
	// IEEE754Compatible mode: the API sends decimals as JSON strings.
	var d Decimal
	err := json.Unmarshal([]byte(`"1.23456"`), &d)
	require.NoError(t, err)
	assert.False(t, d.IsZero())
	assert.Equal(t, "1.23456", d.String())
}

func TestDecimalUnmarshalJSONNumber(t *testing.T) {
	var d Decimal
	err := json.Unmarshal([]byte(`1.5`), &d)
	require.NoError(t, err)
	assert.False(t, d.IsZero())
	assert.Equal(t, "1.5", d.String())
}

func TestDecimalUnmarshalJSONInteger(t *testing.T) {
	var d Decimal
	err := json.Unmarshal([]byte(`42`), &d)
	require.NoError(t, err)
	assert.False(t, d.IsZero())
	assert.Equal(t, "42", d.String())
}

func TestDecimalUnmarshalJSONNull(t *testing.T) {
	var d Decimal
	err := json.Unmarshal([]byte(`null`), &d)
	require.NoError(t, err)
	assert.True(t, d.IsZero())
	assert.Equal(t, "0", d.String())
}

func TestDecimalUnmarshalJSONInvalid(t *testing.T) {
	var d Decimal
	err := json.Unmarshal([]byte(`[1,2,3]`), &d)
	assert.Error(t, err)
}

func TestDecimalMarshalJSONValid(t *testing.T) {
	d := NewDecimal("1.23456")
	data, err := d.MarshalJSON()
	require.NoError(t, err)
	// MarshalJSON always produces a JSON string for IEEE754Compatible mode.
	assert.Equal(t, `"1.23456"`, string(data))
}

func TestDecimalMarshalJSONZero(t *testing.T) {
	var d Decimal
	data, err := d.MarshalJSON()
	require.NoError(t, err)
	assert.Equal(t, `null`, string(data))
}

func TestDecimalMarshalJSONAlwaysString(t *testing.T) {
	// Even integer-looking values should be marshaled as strings.
	d := NewDecimal("42")
	data, err := d.MarshalJSON()
	require.NoError(t, err)
	assert.Equal(t, `"42"`, string(data))
}

func TestDecimalRoundtrip(t *testing.T) {
	tests := []string{"0", "1.23456", "999999999.999999", "-1.5", "0.00"}
	for _, val := range tests {
		t.Run(val, func(t *testing.T) {
			original := NewDecimal(val)
			data, err := json.Marshal(original)
			require.NoError(t, err)

			var roundtripped Decimal
			err = json.Unmarshal(data, &roundtripped)
			require.NoError(t, err)

			assert.Equal(t, original.String(), roundtripped.String())
			assert.Equal(t, original.IsZero(), roundtripped.IsZero())
		})
	}
}

func TestDecimalRoundtripNull(t *testing.T) {
	var original Decimal
	data, err := json.Marshal(original)
	require.NoError(t, err)
	assert.Equal(t, "null", string(data))

	var roundtripped Decimal
	err = json.Unmarshal(data, &roundtripped)
	require.NoError(t, err)
	assert.True(t, roundtripped.IsZero())
}

func TestDecimalInStruct(t *testing.T) {
	type wrapper struct {
		Value Decimal `json:"value"`
	}
	input := `{"value":"3.14"}`
	var w wrapper
	err := json.Unmarshal([]byte(input), &w)
	require.NoError(t, err)
	assert.Equal(t, "3.14", w.Value.String())

	out, err := json.Marshal(w)
	require.NoError(t, err)
	assert.JSONEq(t, `{"value":"3.14"}`, string(out))
}
