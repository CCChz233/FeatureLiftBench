package mapstructure

import "reflect"

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

// Metadata tracks used and unused map keys.
type Metadata struct {
	Unused []string
	Keys   []string
}

// Decoder decodes maps into Go values.
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
	result := reflect.ValueOf(config.Result)
	if result.Kind() != reflect.Pointer || result.IsNil() {
		return nil, &Error{Errors: []string{"result must be a non-nil pointer"}}
	}
	if config.TagName == "" {
		config.TagName = "mapstructure"
	}
	if config.SquashTag == "" {
		config.SquashTag = "squash"
	}
	return &Decoder{config: config}, nil
}

// Decode decodes input into the configured result.
func (d *Decoder) Decode(input interface{}) error {
	target := reflect.ValueOf(d.config.Result).Elem()
	return d.decodeValue("", reflect.ValueOf(input), target)
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
