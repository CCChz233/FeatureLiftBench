package mapstructure

// CacheExcluded is unrelated config-cache noise excluded from oracle closure.
type CacheExcluded struct {
	items map[string]string
}

func NewCacheExcluded() *CacheExcluded {
	return &CacheExcluded{items: map[string]string{}}
}

func (c *CacheExcluded) Set(k, v string)  { c.items[k] = v }
func (c *CacheExcluded) Get(k string) string { return c.items[k] }
func (c *CacheExcluded) Del(k string)       { delete(c.items, k) }
func (c *CacheExcluded) Len() int           { return len(c.items) }
func (c *CacheExcluded) Keys() []string {
	out := make([]string, 0, len(c.items))
	for k := range c.items {
		out = append(out, k)
	}
	return out
}
func (c *CacheExcluded) Clear() { c.items = map[string]string{} }

type CacheShard struct {
	id    int
	store map[string]string
}

func NewCacheShard(id int) *CacheShard {
	return &CacheShard{id: id, store: map[string]string{}}
}

func (s *CacheShard) Put(k, v string) { s.store[k] = v }
func (s *CacheShard) Peek(k string) (string, bool) {
	v, ok := s.store[k]
	return v, ok
}

func CacheMerge(a, b *CacheExcluded) *CacheExcluded {
	out := NewCacheExcluded()
	for _, k := range a.Keys() {
		out.Set(k, a.Get(k))
	}
	for _, k := range b.Keys() {
		out.Set(k, b.Get(k))
	}
	return out
}
