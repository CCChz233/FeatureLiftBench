package mapstructure

import (
	"reflect"
)

// DecoderConfig controls decoder behavior.
type DecoderConfig struct {
	Metadata         *Metadata
	Result           interface{}
	TagName          string
	WeaklyTypedInput bool
	SquashTag        string
	DecodeHook       DecodeHookFunc
	ErrorUnused      bool
}

// Metadata tracks unused keys during decode.
type Metadata struct {
	Unused []string
	Keys   []string
}

// Decoder decodes maps into structs using reflection.
type Decoder struct {
	config *DecoderConfig
}

// NewDecoder returns a decoder for the given configuration.
func NewDecoder(config *DecoderConfig) (*Decoder, error) {
	if config == nil {
		return nil, &Error{Errors: []string{"config must not be nil"}}
	}
	if config.Result == nil {
		return nil, &Error{Errors: []string{"result must be a pointer"}}
	}
	if config.TagName == "" {
		config.TagName = "mapstructure"
	}
	if config.SquashTag == "" {
		config.SquashTag = "squash"
	}
	return &Decoder{config: config}, nil
}

// Decode decodes input into the result configured on the decoder.
func (d *Decoder) Decode(input interface{}) error {
	return d.decode("", input, reflect.ValueOf(d.config.Result).Elem())
}

// Decode is a convenience wrapper around NewDecoder.
func Decode(input, output interface{}) error {
	decoder, err := NewDecoder(&DecoderConfig{Result: output})
	if err != nil {
		return err
	}
	return decoder.Decode(input)
}

// DecodeMetadata decodes with metadata tracking.
func DecodeMetadata(input, output interface{}, metadata *Metadata) error {
	decoder, err := NewDecoder(&DecoderConfig{Result: output, Metadata: metadata})
	if err != nil {
		return err
	}
	return decoder.Decode(input)
}

func (d *Decoder) decode(name string, input interface{}, target reflect.Value) error {
	inputVal := reflect.ValueOf(input)
	if !inputVal.IsValid() {
		return nil
	}
	if d.config.DecodeHook != nil {
		out, err := d.config.DecodeHook(inputVal, target)
		if err != nil {
			return err
		}
		inputVal = reflect.ValueOf(out)
	}
	switch inputVal.Kind() {
	case reflect.Map:
		return d.decodeMap(name, inputVal, target)
	default:
		return d.decodeBasic(name, inputVal, target)
	}
}
