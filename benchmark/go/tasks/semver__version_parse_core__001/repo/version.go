// Package semver is the original source snapshot (read-only).
package semver

import "strings"

type Version struct {
	Major int
	Minor int
	Patch int
	Pre   string
}

func Parse(raw string) (Version, error) {
	raw = Normalize(raw)
	parts := strings.SplitN(raw, "-", 2)
	core := parts[0]
	pre := ""
	if len(parts) == 2 {
		pre = parts[1]
	}
	segments := strings.Split(core, ".")
	if len(segments) != 3 {
		return Version{}, ErrInvalid
	}
	major, err := atoi(segments[0])
	if err != nil {
		return Version{}, ErrInvalid
	}
	minor, err := atoi(segments[1])
	if err != nil {
		return Version{}, ErrInvalid
	}
	patch, err := atoi(segments[2])
	if err != nil {
		return Version{}, ErrInvalid
	}
	return Version{Major: major, Minor: minor, Patch: patch, Pre: pre}, nil
}

func Compare(a, b string) (int, error) {
	va, err := Parse(a)
	if err != nil {
		return 0, err
	}
	vb, err := Parse(b)
	if err != nil {
		return 0, err
	}
	if va.Major != vb.Major {
		return cmpInt(va.Major, vb.Major), nil
	}
	if va.Minor != vb.Minor {
		return cmpInt(va.Minor, vb.Minor), nil
	}
	if va.Patch != vb.Patch {
		return cmpInt(va.Patch, vb.Patch), nil
	}
	return comparePre(va.Pre, vb.Pre), nil
}
