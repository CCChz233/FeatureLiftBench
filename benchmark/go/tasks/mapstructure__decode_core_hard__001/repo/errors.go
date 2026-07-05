package mapstructure

import "fmt"

// Error represents one or more decoder errors.
type Error struct {
	Errors []string
}

func (e *Error) Error() string {
	if len(e.Errors) == 0 {
		return "decode error"
	}
	points := make([]string, len(e.Errors))
	for i, err := range e.Errors {
		points[i] = fmt.Sprintf("* %s", err)
	}
	return fmt.Sprintf("%d error(s) decoding:\n\n%s", len(e.Errors), joinStrings(points, "\n"))
}

func errorf(format string, args ...interface{}) error {
	return &Error{Errors: []string{fmt.Sprintf(format, args...)}}
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
