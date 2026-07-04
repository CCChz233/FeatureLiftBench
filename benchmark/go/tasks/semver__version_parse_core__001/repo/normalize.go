package semver

import "strings"

func Normalize(v string) string {
	v = strings.TrimSpace(v)
	if idx := strings.Index(v, "+"); idx >= 0 {
		v = v[:idx]
	}
	return v
}

func atoi(s string) (int, error) {
	if s == "" {
		return 0, ErrInvalid
	}
	n := 0
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c < '0' || c > '9' {
			return 0, ErrInvalid
		}
		n = n*10 + int(c-'0')
	}
	return n, nil
}
