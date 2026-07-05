package mapstructure

import (
	"fmt"
	"reflect"
	"strconv"
)

func (d *Decoder) decodeValue(name string, input reflect.Value, target reflect.Value) error {
	if !input.IsValid() {
		return nil
	}
	if input.Kind() == reflect.Interface && !input.IsNil() {
		input = input.Elem()
	}
	if !target.CanSet() {
		return errorf("cannot set %s", name)
	}
	if d.config.DecodeHook != nil {
		out, err := d.config.DecodeHook(input, target)
		if err != nil {
			return err
		}
		input = reflect.ValueOf(out)
		if input.IsValid() && input.Kind() == reflect.Interface && !input.IsNil() {
			input = input.Elem()
		}
	}
	if target.Kind() == reflect.Pointer {
		if target.IsNil() {
			target.Set(reflect.New(target.Type().Elem()))
		}
		return d.decodeValue(name, input, target.Elem())
	}
	if ok, err := tryTextUnmarshal(input, target); ok || err != nil {
		return err
	}
	if input.IsValid() && input.Type().AssignableTo(target.Type()) {
		target.Set(input)
		return nil
	}
	if input.IsValid() && input.Type().ConvertibleTo(target.Type()) && target.Kind() != reflect.Struct {
		target.Set(input.Convert(target.Type()))
		return nil
	}
	switch target.Kind() {
	case reflect.Struct:
		_, err := d.decodeStruct(name, input, target)
		return err
	case reflect.Slice:
		return d.decodeSlice(name, input, target)
	case reflect.Map:
		return d.decodeMapValue(name, input, target)
	case reflect.Interface:
		target.Set(input)
		return nil
	default:
		if d.config.WeaklyTypedInput {
			converted, ok, err := weakDecode(input, target.Type())
			if err != nil {
				return errorf("%s: %v", name, err)
			}
			if ok {
				target.Set(converted)
				return nil
			}
		}
	}
	return errorf("type mismatch at %s: %s to %s", name, input.Type(), target.Type())
}

func (d *Decoder) decodeSlice(name string, input reflect.Value, target reflect.Value) error {
	if input.Kind() == reflect.Interface && !input.IsNil() {
		input = input.Elem()
	}
	if input.Kind() != reflect.Slice && input.Kind() != reflect.Array {
		return errorf("expected slice at %s", name)
	}
	out := reflect.MakeSlice(target.Type(), input.Len(), input.Len())
	for i := 0; i < input.Len(); i++ {
		if err := d.decodeValue(fmt.Sprintf("%s[%d]", name, i), input.Index(i), out.Index(i)); err != nil {
			return err
		}
	}
	target.Set(out)
	return nil
}

func (d *Decoder) decodeMapValue(name string, input reflect.Value, target reflect.Value) error {
	if input.Kind() == reflect.Interface && !input.IsNil() {
		input = input.Elem()
	}
	if input.Kind() != reflect.Map {
		return errorf("expected map at %s", name)
	}
	out := reflect.MakeMapWithSize(target.Type(), input.Len())
	for _, key := range input.MapKeys() {
		targetKey := reflect.New(target.Type().Key()).Elem()
		targetVal := reflect.New(target.Type().Elem()).Elem()
		if err := d.decodeValue(name+".key", key, targetKey); err != nil {
			return err
		}
		if err := d.decodeValue(name+"."+fmt.Sprint(key.Interface()), input.MapIndex(key), targetVal); err != nil {
			return err
		}
		out.SetMapIndex(targetKey, targetVal)
	}
	target.Set(out)
	return nil
}

func weakDecode(input reflect.Value, targetType reflect.Type) (reflect.Value, bool, error) {
	if !input.IsValid() {
		return reflect.Value{}, false, nil
	}
	data := input.Interface()
	switch targetType.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		switch v := data.(type) {
		case string:
			n, err := strconv.ParseInt(v, 10, targetType.Bits())
			if err != nil {
				return reflect.Value{}, false, err
			}
			return reflect.ValueOf(n).Convert(targetType), true, nil
		case float64:
			return reflect.ValueOf(int64(v)).Convert(targetType), true, nil
		case float32:
			return reflect.ValueOf(int64(v)).Convert(targetType), true, nil
		}
	case reflect.String:
		return reflect.ValueOf(fmt.Sprint(data)).Convert(targetType), true, nil
	case reflect.Bool:
		if v, ok := data.(string); ok {
			b, err := strconv.ParseBool(v)
			if err != nil {
				return reflect.Value{}, false, err
			}
			return reflect.ValueOf(b), true, nil
		}
	case reflect.Float32, reflect.Float64:
		if v, ok := data.(string); ok {
			n, err := strconv.ParseFloat(v, targetType.Bits())
			if err != nil {
				return reflect.Value{}, false, err
			}
			return reflect.ValueOf(n).Convert(targetType), true, nil
		}
	}
	return reflect.Value{}, false, nil
}
