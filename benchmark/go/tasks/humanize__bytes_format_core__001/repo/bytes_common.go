// Package humanize is the original source snapshot (read-only).
package humanize

import "math"

// IEC Sizes.
const (
	Byte = 1 << (iota * 10)
	KiByte
	MiByte
	GiByte
	TiByte
	PiByte
	EiByte
)

// SI Sizes.
const (
	IByte = 1
	KByte = IByte * 1000
	MByte = KByte * 1000
	GByte = MByte * 1000
	TByte = GByte * 1000
	PByte = TByte * 1000
	EByte = PByte * 1000
)

var bytesSizeTable = map[string]uint64{
	"b":   Byte,
	"kib": KiByte,
	"kb":  KByte,
	"mib": MiByte,
	"mb":  MByte,
	"gib": GiByte,
	"gb":  GByte,
	"tib": TiByte,
	"tb":  TByte,
	"pib": PiByte,
	"pb":  PByte,
	"eib": EiByte,
	"eb":  EByte,
	"":    Byte,
	"ki":  KiByte,
	"k":   KByte,
	"mi":  MiByte,
	"m":   MByte,
	"gi":  GiByte,
	"g":   GByte,
	"ti":  TiByte,
	"t":   TByte,
	"pi":  PiByte,
	"p":   PByte,
	"ei":  EiByte,
	"e":   EByte,
}

func logn(n, b float64) float64 {
	return math.Log(n) / math.Log(b)
}
