package hiddentests

import (
	"testing"

	"featurelifted"
)

func TestPrereleaseOrdering(t *testing.T) {
	cmp, err := featurelifted.Compare("1.0.0-alpha", "1.0.0")
	if err != nil {
		t.Fatal(err)
	}
	if cmp >= 0 {
		t.Fatalf("prerelease should be less than release, got %d", cmp)
	}
}

func TestInvalidVersion(t *testing.T) {
	if _, err := featurelifted.Parse("1.2"); err == nil {
		t.Fatal("expected error for invalid version")
	}
}

func TestBuildMetadataIgnored(t *testing.T) {
	cmp, err := featurelifted.Compare("1.0.0+build", "1.0.0")
	if err != nil {
		t.Fatal(err)
	}
	if cmp != 0 {
		t.Fatalf("build metadata should be ignored, got %d", cmp)
	}
}
