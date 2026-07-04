package publictests

import (
	"testing"

	"featurelifted"
)

type person struct {
	Name string `mapstructure:"name"`
	Age  int    `mapstructure:"age"`
}

func TestDecodeBasicStruct(t *testing.T) {
	var out person
	err := featurelifted.Decode(map[string]any{
		"name": "alice",
		"age":  30,
	}, &out)
	if err != nil {
		t.Fatal(err)
	}
	if out.Name != "alice" || out.Age != 30 {
		t.Fatalf("unexpected: %+v", out)
	}
}

func TestDecodeMetadataKeys(t *testing.T) {
	var out person
	var meta featurelifted.Metadata
	err := featurelifted.DecodeMetadata(map[string]any{"name": "bob", "age": 21}, &out, &meta)
	if err != nil {
		t.Fatal(err)
	}
	if out.Name != "bob" || out.Age != 21 {
		t.Fatalf("unexpected: %+v", out)
	}
}
