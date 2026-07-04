package publictests

import (
	"testing"

	"featurelifted"
)

func TestBytesMegabyte(t *testing.T) {
	if got := featurelifted.Bytes(1024 * 1024); got != "1.0 MB" {
		t.Fatalf("Bytes(1Mi) = %q, want %q", got, "1.0 MB")
	}
}

func TestIBytesMebibyte(t *testing.T) {
	if got := featurelifted.IBytes(1024 * 1024); got != "1.0 MiB" {
		t.Fatalf("IBytes(1MiB) = %q, want %q", got, "1.0 MiB")
	}
}

func TestParseBytesMB(t *testing.T) {
	got, err := featurelifted.ParseBytes("42 MB")
	if err != nil {
		t.Fatal(err)
	}
	if got != 42000000 {
		t.Fatalf("ParseBytes(\"42 MB\") = %d, want 42000000", got)
	}
}
