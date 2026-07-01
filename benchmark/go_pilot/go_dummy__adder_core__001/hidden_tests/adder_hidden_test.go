package featurelifted_test

import (
	"testing"

	flb "featurelifted.local/go_dummy__adder_core__001/featurelifted"
)

func TestAddNegativeAndZero(t *testing.T) {
	cases := []struct {
		a    int
		b    int
		want int
	}{
		{-4, 7, 3},
		{0, 0, 0},
		{-9, -1, -10},
	}
	for _, tc := range cases {
		if got := flb.Add(tc.a, tc.b); got != tc.want {
			t.Fatalf("Add(%d, %d) = %d, want %d", tc.a, tc.b, got, tc.want)
		}
	}
}
