package hiddentests

import (
	"fmt"
	"reflect"
	"testing"

	"featurelifted"
)

type durationMode string

func (m *durationMode) UnmarshalText(text []byte) error {
	switch string(text) {
	case "fast", "safe":
		*m = durationMode(text)
		return nil
	default:
		return fmt.Errorf("bad mode %q", string(text))
	}
}

func TestNestedPointersSlicesAndMaps(t *testing.T) {
	type Limits struct {
		CPU    int      `mapstructure:"cpu"`
		Labels []string `mapstructure:"labels"`
	}
	type Config struct {
		Name   string            `mapstructure:"name"`
		Limits *Limits           `mapstructure:"limits"`
		Ports  []int             `mapstructure:"ports"`
		Tags   map[string]string `mapstructure:"tags"`
	}
	var out Config
	decoder, err := featurelifted.NewDecoder(&featurelifted.DecoderConfig{
		Result:           &out,
		WeaklyTypedInput: true,
	})
	if err != nil {
		t.Fatal(err)
	}
	err = decoder.Decode(map[string]any{
		"name":   "api",
		"limits": map[string]any{"cpu": "4", "labels": []any{"hot", "blue"}},
		"ports":  []any{"80", float64(443)},
		"tags":   map[string]any{"tier": "edge", "team": "platform"},
	})
	if err != nil {
		t.Fatal(err)
	}
	if out.Limits == nil || out.Limits.CPU != 4 || len(out.Limits.Labels) != 2 {
		t.Fatalf("limits = %+v", out.Limits)
	}
	if !reflect.DeepEqual(out.Ports, []int{80, 443}) {
		t.Fatalf("ports = %#v", out.Ports)
	}
	if out.Tags["team"] != "platform" {
		t.Fatalf("tags = %#v", out.Tags)
	}
}

func TestTextUnmarshaler(t *testing.T) {
	var out struct {
		Mode durationMode `mapstructure:"mode"`
	}
	if err := featurelifted.Decode(map[string]any{"mode": "safe"}, &out); err != nil {
		t.Fatal(err)
	}
	if out.Mode != "safe" {
		t.Fatalf("mode = %q", out.Mode)
	}
	if err := featurelifted.Decode(map[string]any{"mode": "unsafe"}, &out); err == nil {
		t.Fatal("expected invalid text value to fail")
	}
}

func TestComposeHookOrder(t *testing.T) {
	var out struct {
		Tags []string `mapstructure:"tags"`
	}
	decoder, err := featurelifted.NewDecoder(&featurelifted.DecoderConfig{
		Result: &out,
		DecodeHook: featurelifted.ComposeDecodeHookFunc(
			featurelifted.DecodeHookFuncType(func(from, to reflect.Type, data interface{}) (interface{}, error) {
				if from.Kind() == reflect.String && to.Kind() == reflect.Slice {
					return data.(string) + ",release", nil
				}
				return data, nil
			}),
			featurelifted.StringToSliceHookFunc(","),
		),
	})
	if err != nil {
		t.Fatal(err)
	}
	if err := decoder.Decode(map[string]any{"tags": "go,lint"}); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(out.Tags, []string{"go", "lint", "release"}) {
		t.Fatalf("tags = %#v", out.Tags)
	}
}

func TestSquashConflictAndUnusedMetadata(t *testing.T) {
	type Left struct {
		Name string `mapstructure:"name"`
	}
	type Right struct {
		Name string `mapstructure:"name"`
	}
	var out struct {
		Left  `mapstructure:",squash"`
		Right `mapstructure:",squash"`
	}
	if err := featurelifted.Decode(map[string]any{"name": "dupe"}, &out); err == nil {
		t.Fatal("expected squash conflict error")
	}

	var meta featurelifted.Metadata
	var single struct {
		Name string `mapstructure:"name"`
	}
	decoder, err := featurelifted.NewDecoder(&featurelifted.DecoderConfig{
		Result:      &single,
		Metadata:    &meta,
		ErrorUnused: true,
	})
	if err != nil {
		t.Fatal(err)
	}
	err = decoder.Decode(map[string]any{"name": "ok", "extra": "nope"})
	if err == nil {
		t.Fatal("expected unused key error")
	}
	if len(meta.Unused) != 1 || meta.Unused[0] != "extra" {
		t.Fatalf("unused metadata = %#v", meta.Unused)
	}
}
