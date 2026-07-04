package publictests

import (
	"testing"

	"featurelifted"
)

func TestParseBasic(t *testing.T) {
	v, err := featurelifted.Parse("1.2.3")
	if err != nil {
		t.Fatal(err)
	}
	if v.Major != 1 || v.Minor != 2 || v.Patch != 3 {
		t.Fatalf("unexpected version: %+v", v)
	}
}

func TestCompareLess(t *testing.T) {
	cmp, err := featurelifted.Compare("1.0.0", "1.0.1")
	if err != nil {
		t.Fatal(err)
	}
	if cmp >= 0 {
		t.Fatalf("want negative compare, got %d", cmp)
	}
}
