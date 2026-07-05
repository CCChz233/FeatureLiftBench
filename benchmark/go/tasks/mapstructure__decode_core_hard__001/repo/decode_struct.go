package mapstructure

import (
	"fmt"
	"reflect"
)

func (d *Decoder) decodeStruct(name string, input reflect.Value, target reflect.Value) (map[string]struct{}, error) {
	if input.Kind() == reflect.Interface {
		input = input.Elem()
	}
	if input.Kind() != reflect.Map {
		return nil, errorf("expected map input for %s", target.Type())
	}
	if target.Kind() != reflect.Struct {
		return nil, errorf("expected struct target at %s", name)
	}

	used := map[string]struct{}{}
	for i := 0; i < target.NumField(); i++ {
		fieldType := target.Type().Field(i)
		if !fieldType.IsExported() {
			continue
		}
		fieldValue := target.Field(i)
		fieldName, squash, skip := decodeFieldInfo(fieldType, d.config.TagName, d.config.SquashTag)
		if skip {
			continue
		}
		if squash {
			if fieldValue.Kind() == reflect.Pointer {
				if fieldValue.IsNil() {
					fieldValue.Set(reflect.New(fieldValue.Type().Elem()))
				}
				fieldValue = fieldValue.Elem()
			}
			nestedUsed, err := d.decodeStruct(name, input, fieldValue)
			if err != nil {
				return nil, err
			}
			for key := range nestedUsed {
				if _, exists := used[key]; exists {
					return nil, errorf("squash conflict for key %q", key)
				}
				used[key] = struct{}{}
			}
			continue
		}
		raw := mapLookup(input, fieldName)
		if !raw.IsValid() {
			continue
		}
		if _, exists := used[fieldName]; exists {
			return nil, errorf("duplicate decode target for key %q", fieldName)
		}
		used[fieldName] = struct{}{}
		if d.config.Metadata != nil {
			d.config.Metadata.Keys = append(d.config.Metadata.Keys, fieldName)
		}
		if err := d.decodeValue(joinName(name, fieldName), raw, fieldValue); err != nil {
			return nil, err
		}
	}

	if d.config.Metadata != nil || d.config.ErrorUnused {
		for _, keyVal := range input.MapKeys() {
			key := fmt.Sprint(keyVal.Interface())
			if _, ok := used[key]; ok {
				continue
			}
			if d.config.Metadata != nil {
				d.config.Metadata.Unused = append(d.config.Metadata.Unused, key)
			}
			if d.config.ErrorUnused {
				return nil, errorf("unused key %q", key)
			}
		}
	}
	return used, nil
}

func decodeFieldInfo(field reflect.StructField, tagName string, squashTag string) (string, bool, bool) {
	tag := field.Tag.Get(tagName)
	if tag == "-" {
		return "", false, true
	}
	name := tag
	opts := ""
	if comma := indexByte(tag, ','); comma >= 0 {
		name = tag[:comma]
		opts = tag[comma+1:]
	}
	squash := containsToken(opts, squashTag)
	if name == "" {
		name = field.Name
	}
	return name, squash, false
}

func mapLookup(input reflect.Value, key string) reflect.Value {
	if input.Type().Key().Kind() == reflect.String {
		return input.MapIndex(reflect.ValueOf(key).Convert(input.Type().Key()))
	}
	for _, keyVal := range input.MapKeys() {
		if fmt.Sprint(keyVal.Interface()) == key {
			return input.MapIndex(keyVal)
		}
	}
	return reflect.Value{}
}

func joinName(prefix string, key string) string {
	if prefix == "" {
		return key
	}
	return prefix + "." + key
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
		if trimSpace(opts[start:end]) == token {
			return true
		}
		if end >= len(opts) {
			break
		}
		start = end + 1
	}
	return false
}
