package mapstructure

import "reflect"

// DecodeHookFunc is a function that transforms a source value before decoding.
type DecodeHookFunc func(from reflect.Value, to reflect.Value) (interface{}, error)

// DecodeHookFuncType is a DecodeHookFunc with explicit types.
type DecodeHookFuncType func(reflect.Type, reflect.Type, interface{}) (interface{}, error)

// DecodeHookFuncValue is a DecodeHookFunc with explicit values.
type DecodeHookFuncValue func(from reflect.Value, to reflect.Value) (interface{}, error)

// ComposeDecodeHookFunc composes multiple decode hooks.
func ComposeDecodeHookFunc(fs ...interface{}) DecodeHookFunc {
	hooks := make([]DecodeHookFunc, 0, len(fs))
	for _, raw := range fs {
		switch f := raw.(type) {
		case DecodeHookFunc:
			hooks = append(hooks, f)
		case DecodeHookFuncType:
			hooks = append(hooks, func(from, to reflect.Value) (interface{}, error) {
				return f(from.Type(), to.Type(), from.Interface())
			})
		case DecodeHookFuncValue:
			hooks = append(hooks, DecodeHookFunc(f))
		}
	}
	return func(from, to reflect.Value) (interface{}, error) {
		var err error
		data := from.Interface()
		for _, hook := range hooks {
			data, err = hook(from, to)
			if err != nil {
				return nil, err
			}
			from = reflect.ValueOf(data)
		}
		return data, nil
	}
}

// StringToSliceHookFunc converts a comma-separated string to []string.
func StringToSliceHookFunc(sep string) DecodeHookFuncType {
	return func(f reflect.Type, t reflect.Type, data interface{}) (interface{}, error) {
		if f.Kind() != reflect.String || t.Kind() != reflect.Slice {
			return data, nil
		}
		if t.Elem().Kind() != reflect.String {
			return data, nil
		}
		raw := data.(string)
		if raw == "" {
			return []string{}, nil
		}
		parts := splitTrim(raw, sep)
		return parts, nil
	}
}

func splitTrim(s, sep string) []string {
	chunks := make([]string, 0)
	start := 0
	for i := 0; i <= len(s); i++ {
		if i == len(s) || s[i:i+len(sep)] == sep {
			part := trimSpace(s[start:i])
			if part != "" {
				chunks = append(chunks, part)
			}
			start = i + len(sep)
			i += len(sep) - 1
		}
	}
	return chunks
}

func trimSpace(s string) string {
	for len(s) > 0 && (s[0] == ' ' || s[0] == '\t') {
		s = s[1:]
	}
	for len(s) > 0 && (s[len(s)-1] == ' ' || s[len(s)-1] == '\t') {
		s = s[:len(s)-1]
	}
	return s
}
