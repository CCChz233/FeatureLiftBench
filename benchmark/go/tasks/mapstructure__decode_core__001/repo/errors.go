// Package mapstructure is the original source snapshot (read-only).
package mapstructure

import "fmt"

// Error represents a mapstructure decoder error.
type Error struct {
	Errors []string
}

func (e *Error) Error() string {
	points := make([]string, len(e.Errors))
	for i, err := range e.Errors {
		points[i] = fmt.Sprintf("* %s", err)
	}
	return fmt.Sprintf("%d error(s) decoding:\n\n%s", len(e.Errors), joinStrings(points, "\n"))
}

func joinStrings(parts []string, sep string) string {
	if len(parts) == 0 {
		return ""
	}
	out := parts[0]
	for _, p := range parts[1:] {
		out += sep + p
	}
	return out
}
