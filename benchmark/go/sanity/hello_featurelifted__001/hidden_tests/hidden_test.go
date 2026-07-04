package hiddentests

import (
	"testing"

	"featurelifted"
)

func TestNegativeAddition(t *testing.T) {
	if got := featurelifted.Add(-1, 5); got != 4 {
		t.Fatalf("Add(-1,5) = %d, want 4", got)
	}
}

func TestZeroAddition(t *testing.T) {
	if got := featurelifted.Add(0, 0); got != 0 {
		t.Fatalf("Add(0,0) = %d, want 0", got)
	}
}

func TestMixedNegative(t *testing.T) {
	if got := featurelifted.Add(-3, -2); got != -5 {
		t.Fatalf("Add(-3,-2) = %d, want -5", got)
	}
}
