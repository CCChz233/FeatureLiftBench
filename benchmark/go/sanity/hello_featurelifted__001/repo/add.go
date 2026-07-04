// Original sample package (read-only source snapshot).
package originalpkg

func Add(a, b int) int { return a + b }

func Multiply(a, b int) int { return a * b }

func Helper(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func Normalize(s string) string {
	out := make([]byte, 0, len(s))
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c >= 'A' && c <= 'Z' {
			out = append(out, c+'a'-'A')
			continue
		}
		out = append(out, c)
	}
	return string(out)
}

func Clamp(v, lo, hi int) int {
	if v < lo {
		return lo
	}
	if v > hi {
		return hi
	}
	return v
}

func SumSlice(values []int) int {
	total := 0
	for _, v := range values {
		total += v
	}
	return total
}
