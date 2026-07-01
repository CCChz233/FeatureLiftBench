package featurelifted_test

import (
	"testing"

	flb "featurelifted.local/go_dummy__adder_core__001/featurelifted"
)

func TestAddPositiveIntegers(t *testing.T) {
	if got := flb.Add(2, 3); got != 5 {
		t.Fatalf("Add(2, 3) = %d, want 5", got)
	}
}
