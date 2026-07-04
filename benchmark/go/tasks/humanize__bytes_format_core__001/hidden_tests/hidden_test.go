package hiddentests

import (
	"testing"

	"featurelifted"
)

func TestParseBytesComma(t *testing.T) {
	got, err := featurelifted.ParseBytes("1,005.03 MB")
	if err != nil {
		t.Fatal(err)
	}
	if got != 1005030000 {
		t.Fatalf("ParseBytes comma = %d, want 1005030000", got)
	}
}

func TestParseBytesCompactIEC(t *testing.T) {
	got, err := featurelifted.ParseBytes("42mib")
	if err != nil {
		t.Fatal(err)
	}
	if got != 44040192 {
		t.Fatalf("ParseBytes(\"42mib\") = %d, want 44040192", got)
	}
}

func TestBytesKiloRounding(t *testing.T) {
	if got := featurelifted.Bytes(9999); got != "10 kB" {
		t.Fatalf("Bytes(9999) = %q, want %q", got, "10 kB")
	}
}

func TestParseBytesOverflow(t *testing.T) {
	if _, err := featurelifted.ParseBytes("16 EiB"); err == nil {
		t.Fatal("expected overflow error for 16 EiB")
	}
}
