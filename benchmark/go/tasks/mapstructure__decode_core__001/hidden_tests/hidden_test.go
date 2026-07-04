package hiddentests

import (
	"testing"

	"featurelifted"
)

func TestWeaklyTypedInput(t *testing.T) {
	var out struct {
		Count int `mapstructure:"count"`
	}
	decoder, err := featurelifted.NewDecoder(&featurelifted.DecoderConfig{
		Result:           &out,
		WeaklyTypedInput: true,
	})
	if err != nil {
		t.Fatal(err)
	}
	if err := decoder.Decode(map[string]any{"count": "42"}); err != nil {
		t.Fatal(err)
	}
	if out.Count != 42 {
		t.Fatalf("count=%d want 42", out.Count)
	}
}

func TestSquashEmbeddedStruct(t *testing.T) {
	type Inner struct {
		Role string `mapstructure:"role"`
	}
	var out struct {
		Inner `mapstructure:",squash"`
		Name  string `mapstructure:"name"`
	}
	err := featurelifted.Decode(map[string]any{
		"name": "carol",
		"role": "admin",
	}, &out)
	if err != nil {
		t.Fatal(err)
	}
	if out.Name != "carol" || out.Inner.Role != "admin" {
		t.Fatalf("unexpected: name=%s role=%s", out.Name, out.Inner.Role)
	}
}

func TestStringToSliceHook(t *testing.T) {
	var out struct {
		Tags []string `mapstructure:"tags"`
	}
	decoder, err := featurelifted.NewDecoder(&featurelifted.DecoderConfig{
		Result: &out,
		DecodeHook: featurelifted.ComposeDecodeHookFunc(
			featurelifted.StringToSliceHookFunc(","),
		),
	})
	if err != nil {
		t.Fatal(err)
	}
	if err := decoder.Decode(map[string]any{"tags": "go,lint,fmt"}); err != nil {
		t.Fatal(err)
	}
	if len(out.Tags) != 3 || out.Tags[0] != "go" {
		t.Fatalf("tags=%v", out.Tags)
	}
}

func TestErrorUnusedKey(t *testing.T) {
	var out struct {
		Name string `mapstructure:"name"`
	}
	decoder, err := featurelifted.NewDecoder(&featurelifted.DecoderConfig{
		Result:      &out,
		ErrorUnused: true,
	})
	if err != nil {
		t.Fatal(err)
	}
	err = decoder.Decode(map[string]any{"name": "dave", "extra": "x"})
	if err == nil {
		t.Fatal("expected unused key error")
	}
}
