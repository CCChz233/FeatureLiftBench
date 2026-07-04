package publictests

import (
	"testing"

	"featurelifted"
)

func TestAddPositive(t *testing.T) {
	if got := featurelifted.Add(1, 2); got != 3 {
		t.Fatalf("Add(1,2) = %d, want 3", got)
	}
}

func TestAddAnother(t *testing.T) {
	if got := featurelifted.Add(10, 5); got != 15 {
		t.Fatalf("Add(10,5) = %d, want 15", got)
	}
}
