package mapstructure

import (
	"encoding"
	"reflect"
)

var textUnmarshalerType = reflect.TypeOf((*encoding.TextUnmarshaler)(nil)).Elem()

func tryTextUnmarshal(input reflect.Value, target reflect.Value) (bool, error) {
	if !input.IsValid() || input.Kind() != reflect.String {
		return false, nil
	}
	if target.CanAddr() {
		addr := target.Addr()
		if addr.Type().Implements(textUnmarshalerType) {
			err := addr.Interface().(encoding.TextUnmarshaler).UnmarshalText([]byte(input.String()))
			return true, err
		}
	}
	if target.Kind() == reflect.Pointer && target.Type().Implements(textUnmarshalerType) {
		if target.IsNil() {
			target.Set(reflect.New(target.Type().Elem()))
		}
		err := target.Interface().(encoding.TextUnmarshaler).UnmarshalText([]byte(input.String()))
		return true, err
	}
	return false, nil
}
