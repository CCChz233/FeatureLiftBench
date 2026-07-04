package mapstructure

import (
	"fmt"
	"reflect"
	"strconv"
)

func (d *Decoder) decodeMap(name string, input reflect.Value, target reflect.Value) error {
	if target.Kind() != reflect.Struct {
		return &Error{Errors: []string{fmt.Sprintf("expected struct target for map at %s", name)}}
	}
	used := map[string]struct{}{}
	for i := 0; i < target.NumField(); i++ {
		field := target.Type().Field(i)
		if !field.IsExported() {
			continue
		}
		tag := field.Tag.Get(d.config.TagName)
		if tag == "-" {
			continue
		}
		squash := false
		if tag == "" {
			tag = field.Name
		} else if idx := indexByte(tag, ','); idx >= 0 {
			opts := tag[idx+1:]
			tag = tag[:idx]
			if containsToken(opts, d.config.SquashTag) {
				squash = true
			}
			if tag == "" && field.Anonymous && !squash {
				tag = field.Name
			}
		}
		if squash {
			if err := d.decodeMap(name, input, target.Field(i)); err != nil {
				return err
			}
			continue
		}
		raw := input.MapIndex(reflect.ValueOf(tag))
		if !raw.IsValid() {
			continue
		}
		used[tag] = struct{}{}
		if d.config.Metadata != nil {
			d.config.Metadata.Keys = append(d.config.Metadata.Keys, tag)
		}
		if err := d.decode(name+"."+tag, raw.Interface(), target.Field(i)); err != nil {
			return err
		}
	}
	if d.config.Metadata != nil || d.config.ErrorUnused {
		for _, keyVal := range input.MapKeys() {
			key := fmt.Sprint(keyVal.Interface())
			if _, ok := used[key]; !ok {
				if d.config.Metadata != nil {
					d.config.Metadata.Unused = append(d.config.Metadata.Unused, key)
				}
				if d.config.ErrorUnused {
					return &Error{Errors: []string{fmt.Sprintf("unused key %q", key)}}
				}
			}
		}
	}
	return nil
}

func (d *Decoder) decodeBasic(name string, input reflect.Value, target reflect.Value) error {
	if !target.CanSet() {
		return &Error{Errors: []string{fmt.Sprintf("cannot set %s", name)}}
	}
	if input.Type().AssignableTo(target.Type()) {
		target.Set(input)
		return nil
	}
	if d.config.WeaklyTypedInput {
		converted, err := weakDecode(input, target.Type())
		if err != nil {
			return &Error{Errors: []string{fmt.Sprintf("%s: %v", name, err)}}
		}
		target.Set(converted)
		return nil
	}
	return &Error{Errors: []string{fmt.Sprintf("type mismatch at %s", name)}}
}

func weakDecode(input reflect.Value, targetType reflect.Type) (reflect.Value, error) {
	data := input.Interface()
	switch targetType.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		switch v := data.(type) {
		case string:
			n, err := strconv.ParseInt(v, 10, 64)
			if err != nil {
				return reflect.Value{}, err
			}
			return reflect.ValueOf(int(n)).Convert(targetType), nil
		case float64:
			return reflect.ValueOf(int(v)).Convert(targetType), nil
		}
	case reflect.String:
		return reflect.ValueOf(fmt.Sprint(data)).Convert(targetType), nil
	case reflect.Bool:
		switch v := data.(type) {
		case string:
			b, err := strconv.ParseBool(v)
			if err != nil {
				return reflect.Value{}, err
			}
			return reflect.ValueOf(b), nil
		}
	}
	return reflect.Value{}, fmt.Errorf("unsupported weak conversion from %T to %s", data, targetType.Kind())
}

func indexByte(s string, b byte) int {
	for i := 0; i < len(s); i++ {
		if s[i] == b {
			return i
		}
	}
	return -1
}

func containsToken(opts, token string) bool {
	start := 0
	for start <= len(opts) {
		end := start
		for end < len(opts) && opts[end] != ',' {
			end++
		}
		part := trimSpace(opts[start:end])
		if part == token {
			return true
		}
		if end >= len(opts) {
			break
		}
		start = end + 1
	}
	return false
}
