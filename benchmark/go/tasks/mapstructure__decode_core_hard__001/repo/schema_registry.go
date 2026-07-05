package mapstructure

// schemaRule describes a decoded field expected by higher-level config code.
type schemaRule struct {
	Key      string
	Kind     string
	Required bool
}

type schemaRegistry struct {
	rules []schemaRule
}

func newSchemaRegistry() *schemaRegistry {
	return &schemaRegistry{rules: []schemaRule{}}
}

func (r *schemaRegistry) Add(key string, kind string, required bool) {
	r.rules = append(r.rules, schemaRule{Key: key, Kind: kind, Required: required})
}

func (r *schemaRegistry) RequiredKeys() []string {
	out := []string{}
	for _, rule := range r.rules {
		if rule.Required {
			out = append(out, rule.Key)
		}
	}
	return out
}

func (r *schemaRegistry) Has(key string) bool {
	for _, rule := range r.rules {
		if rule.Key == key {
			return true
		}
	}
	return false
}

func (r *schemaRegistry) Clone() *schemaRegistry {
	out := newSchemaRegistry()
	out.rules = append(out.rules, r.rules...)
	return out
}
