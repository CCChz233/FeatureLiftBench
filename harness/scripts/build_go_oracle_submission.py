#!/usr/bin/env python3
"""Build Go oracle/naive/copy_all submissions from task repo snapshots."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from featureliftbench.paths import SUBMISSIONS_DIR

_SOURCE_PACKAGES = (
    "package originalpkg",
    "package semver",
    "package humanize",
    "package mapstructure",
)
_ORACLE_EXCLUDED = (
    "bulk_excluded.go",
    "bulk2_excluded.go",
    "bulk3_excluded.go",
    "more_excluded.go",
    "constraints.go",
    "times.go",
    "comma.go",
    "cache_excluded.go",
    "decode_fields.go",
    "decode_plan.go",
    "decode_registry.go",
    "field_cache.go",
    "schema_registry.go",
)

_READY_TASKS = (
    "humanize__bytes_format_core__001",
    "mapstructure__decode_core__001",
    "mapstructure__decode_core_hard__001",
    "semver__version_parse_core__001",
)

_NAIVE_SOURCES: dict[str, dict[str, str]] = {
    "semver__version_parse_core__001": {
        "semver.go": """package featurelifted
import ("errors"; "strconv"; "strings")
type Version struct{ Major, Minor, Patch int }
var ErrInvalid = errors.New("invalid semver")
func Parse(raw string) (Version, error) { p := strings.Split(strings.TrimSpace(raw), "."); if len(p) != 3 { return Version{}, ErrInvalid }; a, e := strconv.Atoi(p[0]); if e != nil { return Version{}, ErrInvalid }; b, e := strconv.Atoi(p[1]); if e != nil { return Version{}, ErrInvalid }; c, e := strconv.Atoi(p[2]); if e != nil { return Version{}, ErrInvalid }; return Version{a, b, c}, nil }
func Compare(a, b string) (int, error) { va, e := Parse(a); if e != nil { return 0, e }; vb, e := Parse(b); if e != nil { return 0, e }; if va.Major != vb.Major { return cmp(va.Major, vb.Major), nil }; if va.Minor != vb.Minor { return cmp(va.Minor, vb.Minor), nil }; return cmp(va.Patch, vb.Patch), nil }
func cmp(a, b int) int { if a < b { return -1 }; if a > b { return 1 }; return 0 }
""",
    },
    "humanize__bytes_format_core__001": {
        "humanize.go": """package featurelifted
import ("fmt"; "strconv"; "strings")
func Bytes(s uint64) string { if s < 10 { return fmt.Sprintf("%d B", s) }; if s >= 1000*1000 { return fmt.Sprintf("%.1f MB", float64(s)/1000/1000) }; return fmt.Sprintf("%.1f kB", float64(s)/1000) }
func IBytes(s uint64) string { if s < 10 { return fmt.Sprintf("%d B", s) }; if s >= 1024*1024 { return fmt.Sprintf("%.1f MiB", float64(s)/1024/1024) }; return fmt.Sprintf("%.1f KiB", float64(s)/1024) }
func ParseBytes(s string) (uint64, error) { fields := strings.Fields(s); if len(fields) != 2 { return 0, fmt.Errorf("invalid byte size") }; n, err := strconv.ParseFloat(fields[0], 64); if err != nil { return 0, err }; switch strings.ToUpper(fields[1]) { case "B": return uint64(n), nil; case "KB": return uint64(n * 1000), nil; case "MB": return uint64(n * 1000 * 1000), nil; default: return 0, fmt.Errorf("unsupported suffix") } }
""",
    },
    "mapstructure__decode_core__001": {
        "mapstructure.go": """package featurelifted
import ("fmt"; "reflect"; "strings")
type DecodeHookFunc func(from reflect.Value, to reflect.Value) (interface{}, error)
type DecodeHookFuncType func(from reflect.Type, to reflect.Type, data interface{}) (interface{}, error)
type DecoderConfig struct{ Metadata *Metadata; Result interface{}; TagName string; WeaklyTypedInput bool; SquashTag string; DecodeHook DecodeHookFunc; ErrorUnused bool }
type Metadata struct{ Unused, Keys []string }
type Decoder struct{ config *DecoderConfig }
func NewDecoder(c *DecoderConfig) (*Decoder, error) { if c == nil || c.Result == nil { return nil, fmt.Errorf("result must be configured") }; if c.TagName == "" { c.TagName = "mapstructure" }; return &Decoder{config: c}, nil }
func (d *Decoder) Decode(input interface{}) error { return decodeMap(input, d.config.Result, d.config.Metadata, d.config.TagName) }
func Decode(input, output interface{}) error { return decodeMap(input, output, nil, "mapstructure") }
func DecodeMetadata(input, output interface{}, metadata *Metadata) error { return decodeMap(input, output, metadata, "mapstructure") }
func ComposeDecodeHookFunc(fs ...interface{}) DecodeHookFunc { return func(from reflect.Value, to reflect.Value) (interface{}, error) { return from.Interface(), nil } }
func StringToSliceHookFunc(sep string) DecodeHookFuncType { return func(from reflect.Type, to reflect.Type, data interface{}) (interface{}, error) { if from.Kind() == reflect.String && to.Kind() == reflect.Slice { return strings.Split(data.(string), sep), nil }; return data, nil } }
func decodeMap(input, output interface{}, metadata *Metadata, tagName string) error { m, ok := input.(map[string]any); if !ok { return fmt.Errorf("input must be map[string]any") }; target := reflect.ValueOf(output); if target.Kind() != reflect.Pointer || target.Elem().Kind() != reflect.Struct { return fmt.Errorf("output must be pointer to struct") }; value := target.Elem(); typeInfo := value.Type(); for i := 0; i < value.NumField(); i++ { field := typeInfo.Field(i); if !field.IsExported() { continue }; name := field.Tag.Get(tagName); if comma := strings.IndexByte(name, ','); comma >= 0 { name = name[:comma] }; if name == "" { name = field.Name }; raw, ok := m[name]; if !ok { continue }; if metadata != nil { metadata.Keys = append(metadata.Keys, name) }; rawValue := reflect.ValueOf(raw); if !rawValue.Type().AssignableTo(value.Field(i).Type()) { return fmt.Errorf("type mismatch for %s", name) }; value.Field(i).Set(rawValue) }; return nil }
""",
    },
}

_COPY_ALL_COMPAT_SOURCES: dict[str, dict[str, str]] = {
    "humanize__bytes_format_core__001": {
        "copy_all_compat.go": """package featurelifted
import "math/big"
func stripTrailingDigits(s string, decimals int) string { if decimals < 0 { return s }; dot := -1; for i, r := range s { if r == '.' { dot = i; break } }; if dot < 0 || dot+1+decimals >= len(s) { return s }; if decimals == 0 { return s[:dot] }; return s[:dot+1+decimals] }
func oom(n *big.Int, b *big.Int) (*big.Int, int) { if n == nil || b == nil || b.Sign() <= 0 { return big.NewInt(0), 0 }; c := new(big.Int).Abs(new(big.Int).Set(n)); i := 0; for c.Cmp(b) >= 0 { c.Div(c, b); i++ }; return c, i }
""",
    },
}

_NAIVE_SOURCES["mapstructure__decode_core_hard__001"] = _NAIVE_SOURCES[
    "mapstructure__decode_core__001"
]


def build_go_submission(task_dir: Path, *, variant: str = "oracle") -> Path:
    task_id = task_dir.name
    repo_dir = task_dir / "repo"
    out_dir = SUBMISSIONS_DIR / task_id / variant
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if variant == "naive":
        naive_files = _NAIVE_SOURCES.get(task_id)
        if naive_files is None:
            raise SystemExit(f"no Go naive source registered for {task_id}")
        for name, text in naive_files.items():
            (out_dir / name).write_text(text, encoding="utf-8")
    else:
        for path in sorted(repo_dir.glob("*.go")):
            text = _rewrite_package(path.read_text(encoding="utf-8"))
            (out_dir / path.name).write_text(text, encoding="utf-8")

        if variant == "oracle":
            for name in _ORACLE_EXCLUDED:
                extra = out_dir / name
                if extra.is_file():
                    extra.unlink()
        elif variant == "copy_all":
            for name, text in _COPY_ALL_COMPAT_SOURCES.get(task_id, {}).items():
                (out_dir / name).write_text(text, encoding="utf-8")

    (out_dir / "go.mod").write_text(
        f"module {_module_path(task_dir)}\n\ngo 1.22\n",
        encoding="utf-8",
    )
    return out_dir


def _rewrite_package(text: str) -> str:
    for src_pkg in _SOURCE_PACKAGES:
        text = text.replace(src_pkg, "package featurelifted")
    return re.sub(r"^package\s+\w+", "package featurelifted", text, count=1, flags=re.MULTILINE)


def _module_path(task_dir: Path) -> str:
    metadata_path = task_dir / "metadata.json"
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        environment = metadata.get("environment")
        if isinstance(environment, dict):
            module_path = environment.get("module_path")
            if isinstance(module_path, str) and module_path:
                return module_path
    return "featurelifted"


def _task_dir_for(task_id: str) -> Path:
    for root in (
        Path("benchmark/go/tasks"),
        Path("benchmark/go/staging"),
        Path("benchmark/go/sanity"),
    ):
        task_dir = root / task_id
        if task_dir.is_dir():
            return task_dir
    raise SystemExit(f"task dir not found for {task_id}")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", type=Path, help="Task directory")
    parser.add_argument(
        "--variant",
        choices=("oracle", "naive", "copy_all", "all"),
        default="oracle",
        help="Submission variant to build",
    )
    parser.add_argument(
        "--all-ready",
        action="store_true",
        help="Build all curated Go gold-candidate tasks",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for one task/variant",
    )
    args = parser.parse_args()

    if args.all_ready:
        if args.output:
            raise SystemExit("--output cannot be used with --all-ready")
        task_dirs = [_task_dir_for(task_id).resolve() for task_id in _READY_TASKS]
    else:
        if args.task is None:
            raise SystemExit("--task is required unless --all-ready is set")
        task_dirs = [args.task.resolve()]

    variants = ("oracle", "naive", "copy_all") if args.variant == "all" else (args.variant,)
    out = None
    for task_dir in task_dirs:
        for variant in variants:
            out = build_go_submission(task_dir, variant=variant)
            print(f"built {out}")

    if args.output:
        if len(task_dirs) != 1 or len(variants) != 1:
            raise SystemExit("--output requires exactly one task and one variant")
        import shutil

        args.output = args.output.resolve()
        if args.output.exists():
            shutil.rmtree(args.output)
        assert out is not None
        shutil.copytree(out, args.output)
        out = args.output
        print(f"copied {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
