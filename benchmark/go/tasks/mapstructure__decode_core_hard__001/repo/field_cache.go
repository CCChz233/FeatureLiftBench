package mapstructure

// fieldCache stores reflection field plans by source type.
type fieldCache struct {
	byType map[string][]cachedField
}

type cachedField struct {
	Name      string
	Index     int
	Squashed  bool
	OmitEmpty bool
}

func newFieldCache() *fieldCache {
	return &fieldCache{byType: map[string][]cachedField{}}
}

func (c *fieldCache) Get(typeName string) ([]cachedField, bool) {
	fields, ok := c.byType[typeName]
	return fields, ok
}

func (c *fieldCache) Put(typeName string, fields []cachedField) {
	c.byType[typeName] = append([]cachedField(nil), fields...)
}

func (c *fieldCache) Delete(typeName string) {
	delete(c.byType, typeName)
}

func (c *fieldCache) Len() int {
	return len(c.byType)
}

func (c *fieldCache) Keys() []string {
	out := make([]string, 0, len(c.byType))
	for key := range c.byType {
		out = append(out, key)
	}
	return out
}

func mergeFieldCaches(left, right *fieldCache) *fieldCache {
	out := newFieldCache()
	if left != nil {
		for _, key := range left.Keys() {
			fields, _ := left.Get(key)
			out.Put(key, fields)
		}
	}
	if right != nil {
		for _, key := range right.Keys() {
			fields, _ := right.Get(key)
			out.Put(key, fields)
		}
	}
	return out
}
