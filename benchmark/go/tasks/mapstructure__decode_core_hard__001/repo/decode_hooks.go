package mapstructure

import "reflect"

// DecodeHookFunc transforms a source value before decoding.
type DecodeHookFunc func(from reflect.Value, to reflect.Value) (interface{}, error)

// DecodeHookFuncType is a hook written in terms of source/target types.
type DecodeHookFuncType func(reflect.Type, reflect.Type, interface{}) (interface{}, error)

// DecodeHookFuncValue is a hook written in terms of source/target values.
type DecodeHookFuncValue func(from reflect.Value, to reflect.Value) (interface{}, error)

// ComposeDecodeHookFunc composes hooks in the order provided.
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
		current := from
		for _, hook := range hooks {
			data, err = hook(current, to)
			if err != nil {
				return nil, err
			}
			current = reflect.ValueOf(data)
		}
		return data, nil
	}
}

// StringToSliceHookFunc converts a delimited string into a []string.
func StringToSliceHookFunc(sep string) DecodeHookFuncType {
	return func(f reflect.Type, t reflect.Type, data interface{}) (interface{}, error) {
		if f.Kind() != reflect.String || t.Kind() != reflect.Slice || t.Elem().Kind() != reflect.String {
			return data, nil
		}
		raw := data.(string)
		if raw == "" {
			return []string{}, nil
		}
		return splitTrim(raw, sep), nil
	}
}

func splitTrim(s, sep string) []string {
	if sep == "" {
		return []string{s}
	}
	out := make([]string, 0)
	start := 0
	for i := 0; i <= len(s)-len(sep); i++ {
		if s[i:i+len(sep)] != sep {
			continue
		}
		if part := trimSpace(s[start:i]); part != "" {
			out = append(out, part)
		}
		start = i + len(sep)
		i += len(sep) - 1
	}
	if part := trimSpace(s[start:]); part != "" {
		out = append(out, part)
	}
	return out
}

func trimSpace(s string) string {
	for len(s) > 0 && (s[0] == ' ' || s[0] == '\t' || s[0] == '\n') {
		s = s[1:]
	}
	for len(s) > 0 && (s[len(s)-1] == ' ' || s[len(s)-1] == '\t' || s[len(s)-1] == '\n') {
		s = s[:len(s)-1]
	}
	return s
}
