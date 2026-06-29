#!/usr/bin/env python3
"""Scaffold batch-1 staging tasks: humanize, isodate, rfc3986, python-box, arrow."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE = Path("/Users/chz/anaconda3/lib/python3.12/site-packages")
STAGING = REPO_ROOT / "benchmark" / "staging"
DESIGNS = REPO_ROOT / "docs" / "task_designs"
SUBMISSIONS = REPO_ROOT / "benchmark" / "submissions"


def copy_pkg_py(src_pkg: Path, dst_pkg: Path, *, extra_dirs: list[str] | None = None) -> None:
    dst_pkg.mkdir(parents=True, exist_ok=True)
    for path in sorted(src_pkg.iterdir()):
        if path.name in {"__pycache__"}:
            continue
        if path.suffix in {".py", ".typed", ".pyi"}:
            shutil.copy2(path, dst_pkg / path.name)
        elif path.is_dir() and extra_dirs and path.name in extra_dirs:
            shutil.copytree(path, dst_pkg / path.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    init = src_pkg / "__init__.py"
    if init.exists() and not (dst_pkg / "__init__.py").exists():
        shutil.copy2(init, dst_pkg / "__init__.py")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_humanize() -> None:
    tid = "humanize__naturaltime_core__001"
    task = STAGING / tid
    copy_pkg_py(SITE / "humanize", task / "repo" / "humanize", extra_dirs=["locale"])
    write_json(task / "metadata.json", {
        "task_id": tid,
        "language": "python",
        "difficulty": "hard",
        "tags": ["batch-1", "humanize", "naturaltime", "hard-first", "functional-discriminator", "data_model_coupling"],
        "source": {"name": "humanize", "url": "https://github.com/python-humanize/humanize", "commit": "4.15.0-installed-snapshot", "license": "MIT"},
        "feature": {
            "name": "Humanize natural time and delta formatting",
            "description": "Extract humanize naturaltime/naturaldelta/naturaldate helpers without importing humanize.",
            "source_entrypoints": ["humanize.time.naturaltime", "humanize.time.naturaldelta", "humanize.time.naturaldate", "humanize.time.naturalday", "humanize.time.precisedelta"],
            "included_behaviors": ["naturaltime relative phrasing with when=", "naturaldelta month/year granularity", "precisedelta suppress and minimum_unit", "naturaldate and naturalday phrasing"],
            "excluded_behaviors": ["filesize/lists/number formatting beyond time deps", "non-English locale packs", "original humanize import at runtime"],
        },
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "implicit_dependency_coupling"],
            "primary": "data_model_coupling",
            "description": "Time humanization couples timedelta quantization, i18n gettext wrappers, and intcomma year formatting.",
            "signals": ["naturaltime tense derives from when= anchor", "precisedelta suppress/minimum_unit alter unit ladder", "naturaldelta months toggles year/month buckets", "naturaldate switches format past ~5 months"],
        },
        "output": {
            "package": "featurelifted",
            "import": "import featurelifted; from featurelifted import naturaltime, naturaldelta, naturaldate, naturalday, precisedelta",
            "callable": "featurelifted.naturaltime",
            "signature": "naturaltime(value, future=False, months=True, minimum_unit='seconds', when=None) -> str",
        },
        "environment": {
            "python": "3.11", "network": False, "timeout_seconds": 60,
            "dependency_lock": "requirements.lock", "allowed_dependencies": [],
            "forbidden_dependencies": ["humanize"], "forbidden_imports": ["humanize"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    })
    write_text(task / "evaluation/forbidden_imports.txt", "humanize\n")
    write_json(task / "evaluation/oracle_manifest.json", {
        "source_package_name": "humanize",
        "required_source_files": ["humanize/time.py", "humanize/i18n.py", "humanize/number.py", "humanize/_version.py"],
        "runtime_dependencies": [],
        "notes": "Oracle is time+i18n+number core; repo includes filesize/lists/locale for copy-all penalty.",
    })
    write_text(task / "requirements.lock", "")
    write_text(task / "public_tests/test_public_api.py", '''from __future__ import annotations

from datetime import datetime, timedelta

from featurelifted import naturaldate, naturaldelta, naturaltime


def test_naturaltime_past_with_when() -> None:
    when = datetime(2020, 1, 15, 12, 0, 0)
    past = when - timedelta(minutes=30)
    assert naturaltime(past, when=when) == "30 minutes ago"


def test_naturaldelta_hours() -> None:
    assert naturaldelta(timedelta(hours=2, minutes=5)) == "2 hours"


def test_naturaldate_distant_year() -> None:
    assert naturaldate(datetime(2020, 1, 1)) == "Jan 01 2020"
''')
    write_text(task / "hidden_tests/test_hidden_behavior.py", '''from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from pathlib import Path

from featurelifted import naturalday, naturaldelta, naturaltime, precisedelta


def test_naturaltime_future_with_when() -> None:
    when = datetime(2020, 1, 15, 12, 0, 0)
    future = when + timedelta(hours=3)
    assert naturaltime(future, when=when) == "3 hours from now"


def test_precisedelta_suppress_days() -> None:
    delta = timedelta(days=2, seconds=33)
    assert precisedelta(delta, minimum_unit="minutes", suppress=["days"]) == "48 hours and 0.55 minutes"


def test_naturaldelta_long_month_granularity() -> None:
    assert naturaldelta(timedelta(days=400), months=True) == "1 year, 1 month"


def test_naturalday_today_label() -> None:
    assert naturalday(date.today()) == "today"


def test_naturaltime_two_hour_past() -> None:
    when = datetime(2020, 6, 1, 12, 0, 0)
    past = when - timedelta(hours=2)
    assert naturaltime(past, when=when) == "2 hours ago"


def test_no_humanize_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(r"^\\s*(?:from humanize|import humanize)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not import_pattern.search(path.read_text(encoding="utf-8"))
''')
    write_text(DESIGNS / f"{tid}.md", f"""# Task Design: `{tid}`

Status: draft

## Practical reuse

1. **Reuse module** — Standalone relative-time phrasing for logs, UI timestamps, and audit trails.
2. **Who imports it** — Apps needing Django-style naturaltime without vendoring all humanize formatters.
3. **Why not copy-all** — Full humanize bundles filesize, lists, number, and locale packs beyond time core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Naturaltime future | `featurelifted/time.py` | `test_naturaltime_future_with_when` |
| Precisedelta suppress | `featurelifted/time.py` | `test_precisedelta_suppress_days` |
| Number intcomma years | `featurelifted/number.py` | `test_naturaldelta_long_month_granularity` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | Flash deferred |
""")
    write_text(SUBMISSIONS / tid / "naive/featurelifted/__init__.py", '''"""Shallow naturaltime stub for FeatureLiftBench naive baseline."""

from __future__ import annotations

from datetime import date, datetime, timedelta


def naturaldelta(delta: timedelta, months: bool = True, minimum_unit: str = "seconds") -> str:
    del months, minimum_unit
    total = int(delta.total_seconds())
    if total >= 86400:
        return f"{total // 86400} days"
    if total >= 3600:
        return f"{total // 3600} hours"
    if total >= 60:
        return f"{total // 60} minutes"
    return f"{total} seconds"


def naturaltime(value: datetime | timedelta | float, future: bool = False, months: bool = True, minimum_unit: str = "seconds", when: datetime | None = None) -> str:
    del future, months, minimum_unit
    if isinstance(value, datetime):
        anchor = when or datetime.now()
        delta = anchor - value
        secs = int(abs(delta.total_seconds()))
        if secs < 60:
            return "now"
        return f"{secs // 60} minutes ago"
    if isinstance(value, timedelta):
        return naturaldelta(value)
    return f"{int(value)} seconds ago"


def naturaldate(value: date | datetime) -> str:
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%b %d %Y")


def naturalday(value: date | datetime, format: str = "%b %d") -> str:
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime(format)


def precisedelta(value: timedelta | float | None, minimum_unit: str = "seconds", suppress: tuple[str, ...] = (), format: str = "%0.2f") -> str:
    del minimum_unit, suppress, format
    if value is None:
        return ""
    if not isinstance(value, timedelta):
        value = timedelta(seconds=float(value))
    return naturaldelta(value)
''')


def scaffold_isodate() -> None:
    tid = "isodate__duration_parse_core__001"
    task = STAGING / tid
    copy_pkg_py(SITE / "isodate", task / "repo" / "isodate")
    write_json(task / "metadata.json", {
        "task_id": tid,
        "language": "python",
        "difficulty": "hard",
        "tags": ["batch-1", "isodate", "duration", "hard-first", "functional-discriminator", "parser_state_coupling"],
        "source": {"name": "isodate", "url": "https://github.com/gweis/isodate", "commit": "0.7.2-installed-snapshot", "license": "BSD-3-Clause"},
        "feature": {
            "name": "ISO8601 duration parse and format",
            "description": "Extract isodate Duration parsing and isoformat helpers without importing isodate.",
            "source_entrypoints": ["isodate.parse_duration", "isodate.duration_isoformat", "isodate.duration.Duration"],
            "included_behaviors": ["parse P-period durations to timedelta or Duration", "duration_isoformat for Duration and timedelta", "decimal comma fractions in components", "ISO8601Error on invalid input"],
            "excluded_behaviors": ["full date/time/tz parsing surface", "strftime locale tables beyond duration chain", "original isodate import at runtime"],
        },
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "data_model_coupling"],
            "primary": "parser_state_coupling",
            "description": "Duration parsing couples regex capture groups, Decimal year/month handling, and Duration vs timedelta selection.",
            "signals": ["years/months force Duration object", "comma decimals normalized in regex groups", "alternative datetime duration delegates to parse_datetime", "duration_isoformat routes through strftime tokens"],
        },
        "output": {
            "package": "featurelifted",
            "import": "import featurelifted; from featurelifted import Duration, ISO8601Error, duration_isoformat, parse_duration",
            "callable": "featurelifted.parse_duration",
            "signature": "parse_duration(datestring, as_timedelta_if_possible=True)",
        },
        "environment": {
            "python": "3.11", "network": False, "timeout_seconds": 60,
            "dependency_lock": "requirements.lock", "allowed_dependencies": [],
            "forbidden_dependencies": ["isodate"], "forbidden_imports": ["isodate"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    })
    write_text(task / "evaluation/forbidden_imports.txt", "isodate\n")
    write_json(task / "evaluation/oracle_manifest.json", {
        "source_package_name": "isodate",
        "required_source_files": [
            "isodate/duration.py", "isodate/isoduration.py", "isodate/isoerror.py",
            "isodate/isodatetime.py", "isodate/isodates.py", "isodate/isotime.py", "isodate/isostrf.py",
        ],
        "runtime_dependencies": [],
        "notes": "Oracle is duration parse/format chain; repo includes tz/time helpers for copy-all penalty.",
    })
    write_text(task / "requirements.lock", "")
    write_text(task / "public_tests/test_public_api.py", '''from __future__ import annotations

from datetime import timedelta

from featurelifted import Duration, duration_isoformat, parse_duration


def test_parse_duration_days_hours() -> None:
    result = parse_duration("P1DT12H")
    assert isinstance(result, timedelta)
    assert result == timedelta(days=1, hours=12)


def test_parse_duration_weeks() -> None:
    result = parse_duration("P2W")
    assert result == timedelta(weeks=2)


def test_duration_isoformat() -> None:
    assert duration_isoformat(Duration(years=1, months=2, days=3)) == "P1Y2M3D"
''')
    write_text(task / "hidden_tests/test_hidden_behavior.py", '''from __future__ import annotations

import re
from datetime import timedelta
from pathlib import Path

import pytest

from featurelifted import Duration, ISO8601Error, duration_isoformat, parse_duration


def test_parse_duration_full_components() -> None:
    result = parse_duration("P1Y2M3DT4H5M6S")
    assert isinstance(result, Duration)
    assert result.years == 1
    assert result.months == 2
    assert result.days == 3
    assert result.hours == 4
    assert result.minutes == 5
    assert result.seconds == 6


def test_parse_duration_comma_decimal_hours() -> None:
    result = parse_duration("PT1,5H")
    assert result == timedelta(hours=1, minutes=30)


def test_duration_totimedelta_with_start() -> None:
    from featurelifted.isodates import parse_date

    d = Duration(years=1, months=1)
    td = d.totimedelta(start=parse_date("2000-03-01"))
    assert td == timedelta(days=31)


def test_duration_isoformat_timedelta() -> None:
    assert duration_isoformat(timedelta(hours=2, minutes=30)) == "PT2H30M"


def test_parse_invalid_raises() -> None:
    with pytest.raises(ISO8601Error):
        parse_duration("not-a-duration")


def test_no_isodate_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(r"^\\s*(?:from isodate|import isodate)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not import_pattern.search(path.read_text(encoding="utf-8"))
''')
    write_text(DESIGNS / f"{tid}.md", f"""# Task Design: `{tid}`

Status: draft

## Practical reuse

1. **Reuse module** — ISO8601 duration parser for APIs, media manifests, and billing intervals.
2. **Who imports it** — Services parsing XML Schema durations without the full isodate datetime stack.
3. **Why not copy-all** — Full isodate bundles date/time/tz parsers and strftime tables beyond duration core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Duration model | `featurelifted/duration.py` | `test_parse_duration_full_components` |
| Period regex | `featurelifted/isoduration.py` | `test_parse_duration_comma_decimal_hours` |
| Date combine | `featurelifted/isodates.py` | `test_duration_totimedelta_with_start` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""")
    write_text(SUBMISSIONS / tid / "naive/featurelifted/__init__.py", '''"""Naive ISO duration stub."""

from __future__ import annotations

import re
from datetime import timedelta

_ISO_SIMPLE = re.compile(r"^P(?:(?P<days>\\d+)D)?(?:T(?:(?P<hours>\\d+)H)?(?:(?P<minutes>\\d+)M)?(?:(?P<seconds>\\d+)S)?)?$")
_ISO_WEEKS = re.compile(r"^P(?P<weeks>\\d+)W$")


class ISO8601Error(ValueError):
    pass


class Duration(timedelta):
    def __init__(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0, months=0, years=0):
        del months, years, milliseconds
        super().__init__(days=days + weeks * 7, seconds=seconds + minutes * 60 + hours * 3600, microseconds=microseconds)


def parse_duration(datestring: str, as_timedelta_if_possible: bool = True) -> Duration | timedelta:
    del as_timedelta_if_possible
    m = _ISO_WEEKS.fullmatch(datestring)
    if m:
        return timedelta(weeks=int(m.group("weeks")))
    m = _ISO_SIMPLE.fullmatch(datestring)
    if not m:
        raise ISO8601Error(datestring)
    return timedelta(
        days=int(m.group("days") or 0),
        hours=int(m.group("hours") or 0),
        minutes=int(m.group("minutes") or 0),
        seconds=int(m.group("seconds") or 0),
    )


def duration_isoformat(value: Duration | timedelta) -> str:
    if isinstance(value, timedelta):
        total = int(value.total_seconds())
        hours, rem = divmod(total, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"PT{hours}H{minutes}M{seconds}S"
    return "P0D"
''')


def scaffold_rfc3986() -> None:
    tid = "rfc3986__uri_parse_core__001"
    task = STAGING / tid
    copy_pkg_py(SITE / "rfc3986", task / "repo" / "rfc3986")
    write_json(task / "metadata.json", {
        "task_id": tid,
        "language": "python",
        "difficulty": "hard",
        "tags": ["batch-1", "rfc3986", "uri", "hard-first", "functional-discriminator", "parser_state_coupling"],
        "source": {"name": "rfc3986", "url": "https://github.com/python-hyper/rfc3986", "commit": "2.0.0-installed-snapshot", "license": "Apache-2.0"},
        "feature": {
            "name": "RFC3986 URI parse, build, and validate subset",
            "description": "Extract rfc3986 URIReference parsing, normalization, and URIBuilder without importing rfc3986.",
            "source_entrypoints": ["rfc3986.uri_reference", "rfc3986.normalize_uri", "rfc3986.is_valid_uri", "rfc3986.builder.URIBuilder"],
            "included_behaviors": ["parse URI components and authority subcomponents", "normalize scheme/host/path", "URIBuilder compose and finalize", "is_valid_uri convenience check"],
            "excluded_behaviors": ["IRI full unicode normalization", "validators beyond basic is_valid_uri", "original rfc3986 import at runtime"],
        },
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "data_model_coupling"],
            "primary": "parser_state_coupling",
            "description": "URI parsing couples ABNF regex groups, namedtuple URIReference, normalizers, and builder mutation.",
            "signals": ["authority splits userinfo/host/port", "normalize_uri lowercases scheme/host", "URIBuilder finalize rebuilds components", "ParseResult urlparse compatibility"],
        },
        "output": {
            "package": "featurelifted",
            "import": "import featurelifted; from featurelifted import URIBuilder, URIReference, is_valid_uri, normalize_uri, uri_reference",
            "callable": "featurelifted.uri_reference",
            "signature": "uri_reference(uri, encoding='utf-8') -> URIReference",
        },
        "environment": {
            "python": "3.11", "network": False, "timeout_seconds": 60,
            "dependency_lock": "requirements.lock", "allowed_dependencies": [],
            "forbidden_dependencies": ["rfc3986"], "forbidden_imports": ["rfc3986"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    })
    write_text(task / "evaluation/forbidden_imports.txt", "rfc3986\n")
    write_json(task / "evaluation/oracle_manifest.json", {
        "source_package_name": "rfc3986",
        "required_source_files": [
            "rfc3986/uri.py", "rfc3986/parseresult.py", "rfc3986/api.py", "rfc3986/misc.py",
            "rfc3986/normalizers.py", "rfc3986/_mixin.py", "rfc3986/compat.py", "rfc3986/exceptions.py",
            "rfc3986/abnf_regexp.py", "rfc3986/builder.py",
        ],
        "runtime_dependencies": [],
        "notes": "Oracle is parse/build/normalize core; repo includes validators/iri for copy-all penalty.",
    })
    write_text(task / "requirements.lock", "")
    write_text(task / "public_tests/test_public_api.py", '''from __future__ import annotations

from featurelifted import URIBuilder, is_valid_uri, uri_reference


def test_uri_reference_components() -> None:
    ref = uri_reference("https://example.com:8080/path?q=1#frag")
    assert ref.scheme == "https"
    assert ref.host == "example.com"
    assert ref.port == 8080
    assert ref.path == "/path"
    assert ref.query == "q=1"
    assert ref.fragment == "frag"


def test_is_valid_uri_https() -> None:
    assert is_valid_uri("https://example.com/path")


def test_uri_builder_finalize() -> None:
    built = URIBuilder().add_scheme("https").add_host("example.com").add_path("/x").finalize()
    assert built.scheme == "https"
    assert built.host == "example.com"
    assert built.path == "/x"
''')
    write_text(task / "hidden_tests/test_hidden_behavior.py", '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import URIBuilder, normalize_uri, uri_reference


def test_authority_userinfo_host_port() -> None:
    ref = uri_reference("https://User:Pass@Example.COM:8080/a")
    assert ref.userinfo == "User:Pass"
    assert ref.host == "Example.COM"
    assert ref.port == 8080


def test_normalize_uri_path_dots() -> None:
    assert normalize_uri("HTTP://EXAMPLE.COM:80/a/../b") == "http://example.com:80/b"


def test_builder_from_uri_roundtrip() -> None:
    ref = uri_reference("https://example.com:443/a?x=1#top")
    rebuilt = URIBuilder.from_uri(ref).finalize()
    assert rebuilt.scheme == "https"
    assert rebuilt.host == "example.com"
    assert rebuilt.path == "/a"
    assert rebuilt.query == "x=1"
    assert rebuilt.fragment == "top"


def test_uri_reference_ipv6_host() -> None:
    ref = uri_reference("http://[::1]:8080/")
    assert ref.host == "::1"
    assert ref.port == 8080


def test_normalize_preserves_fragment() -> None:
    assert normalize_uri("HTTPS://Example.COM/x#frag").endswith("#frag")


def test_no_rfc3986_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(r"^\\s*(?:from rfc3986|import rfc3986)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not import_pattern.search(path.read_text(encoding="utf-8"))
''')
    write_text(DESIGNS / f"{tid}.md", f"""# Task Design: `{tid}`

Status: draft

## Practical reuse

1. **Reuse module** — RFC3986 URI parser/builder for HTTP clients, config URLs, and service discovery.
2. **Who imports it** — Libraries needing hyper/rfc3986 semantics without the validators/IRI extras.
3. **Why not copy-all** — Full package ships IRI and Validator stacks beyond parse/build/normalize core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Authority split | `featurelifted/parseresult.py` | `test_authority_userinfo_host_port` |
| Normalizers | `featurelifted/normalizers.py` | `test_normalize_uri_path_dots` |
| Builder | `featurelifted/builder.py` | `test_builder_from_uri_roundtrip` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""")
    write_text(SUBMISSIONS / tid / "naive/featurelifted/__init__.py", '''"""Naive URI split stub."""

from __future__ import annotations

from collections import namedtuple
from urllib.parse import urlparse, urlunparse

URIReference = namedtuple("URIReference", "scheme authority path query fragment userinfo host port")


def _split_auth(authority: str | None) -> tuple[str | None, str | None, int | None]:
    if not authority:
        return None, None, None
    userinfo = None
    hostport = authority
    if "@" in authority:
        userinfo, hostport = authority.split("@", 1)
    if hostport.startswith("["):
        end = hostport.index("]")
        host = hostport[1:end]
        rest = hostport[end + 1 :]
        port = int(rest[1:]) if rest.startswith(":") else None
        return userinfo, host, port
    if ":" in hostport:
        host, port_s = hostport.rsplit(":", 1)
        return userinfo, host, int(port_s)
    return userinfo, hostport, None


def uri_reference(uri: str, encoding: str = "utf-8") -> URIReference:
    del encoding
    p = urlparse(uri)
    userinfo, host, port = _split_auth(p.netloc)
    return URIReference(p.scheme, p.netloc, p.path, p.query, p.fragment, userinfo, host, port)


def is_valid_uri(uri: str, encoding: str = "utf-8", **kwargs: object) -> bool:
    del encoding, kwargs
    return bool(urlparse(uri).scheme)


def normalize_uri(uri: str, encoding: str = "utf-8") -> str:
    del encoding
    p = urlparse(uri)
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path, p.params, p.query, p.fragment))


class URIBuilder:
    def __init__(self) -> None:
        self._parts = {"scheme": None, "userinfo": None, "host": None, "port": None, "path": None, "query": None, "fragment": None}

    def add_scheme(self, scheme: str) -> "URIBuilder":
        self._parts["scheme"] = scheme
        return self

    def add_host(self, host: str) -> "URIBuilder":
        self._parts["host"] = host
        return self

    def add_path(self, path: str) -> "URIBuilder":
        self._parts["path"] = path
        return self

    def finalize(self) -> URIReference:
        host = self._parts["host"] or ""
        port = self._parts["port"]
        authority = f"{host}:{port}" if port else host
        return URIReference(self._parts["scheme"], authority, self._parts["path"] or "", self._parts["query"], self._parts["fragment"], None, host, port)

    @classmethod
    def from_uri(cls, ref: URIReference) -> "URIBuilder":
        b = cls()
        b._parts.update({"scheme": ref.scheme, "host": ref.host, "port": ref.port, "path": ref.path, "query": ref.query, "fragment": ref.fragment, "userinfo": ref.userinfo})
        return b
''')


def scaffold_python_box() -> None:
    tid = "python_box__config_box_core__001"
    task = STAGING / tid
    copy_pkg_py(SITE / "box", task / "repo" / "box")
    write_json(task / "metadata.json", {
        "task_id": tid,
        "language": "python",
        "difficulty": "hard",
        "tags": ["batch-1", "python-box", "config", "hard-first", "functional-discriminator", "data_model_coupling"],
        "source": {"name": "python-box", "url": "https://github.com/cdgriffith/Box", "commit": "7.4.1-installed-snapshot", "license": "MIT"},
        "feature": {
            "name": "ConfigBox dot-access config transforms",
            "description": "Extract python-box ConfigBox typed accessors without importing box.",
            "source_entrypoints": ["box.config_box.ConfigBox", "box.box.Box"],
            "included_behaviors": ["dot and bracket dict access", "case-insensitive ConfigBox keys", "bool/int/float/list coercion helpers", "default values on missing keys"],
            "excluded_behaviors": ["yaml/toml/msgpack converters and file loaders", "ShorthandBox and BoxList extras", "original box import at runtime"],
        },
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "implicit_dependency_coupling"],
            "primary": "data_model_coupling",
            "description": "ConfigBox couples Box dot-access recursion, case folding, and typed coercion tables.",
            "signals": ["__getattr__ lowercases missing keys", "bool() treats yes/no/false strings", "list() splits comma strings with mod callback", "defaults bypass BoxKeyError"],
        },
        "output": {
            "package": "featurelifted",
            "import": "import featurelifted; from featurelifted import Box, ConfigBox",
            "callable": "featurelifted.ConfigBox",
            "signature": "ConfigBox(*args, **kwargs) -> ConfigBox",
        },
        "environment": {
            "python": "3.11", "network": False, "timeout_seconds": 60,
            "dependency_lock": "requirements.lock", "allowed_dependencies": [],
            "forbidden_dependencies": ["python-box", "box"], "forbidden_imports": ["box"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    })
    write_text(task / "evaluation/forbidden_imports.txt", "box\n")
    write_json(task / "evaluation/oracle_manifest.json", {
        "source_package_name": "box",
        "required_source_files": ["box/box.py", "box/config_box.py", "box/exceptions.py"],
        "runtime_dependencies": [],
        "notes": "Oracle is Box+ConfigBox core with stub converters; repo includes converters/from_file/shorthand for copy-all penalty.",
    })
    write_text(task / "requirements.lock", "")
    write_text(task / "public_tests/test_public_api.py", '''from __future__ import annotations

from featurelifted import ConfigBox


def test_dot_access() -> None:
    cfg = ConfigBox(host="localhost", port="8080")
    assert cfg.host == "localhost"
    assert cfg.port == "8080"


def test_bool_yes_no() -> None:
    cfg = ConfigBox(enabled="yes", disabled="no")
    assert cfg.bool("enabled") is True
    assert cfg.bool("disabled") is False


def test_int_coercion() -> None:
    cfg = ConfigBox(retries="3")
    assert cfg.int("retries") == 3
''')
    write_text(task / "hidden_tests/test_hidden_behavior.py", '''from __future__ import annotations

import re
from pathlib import Path

import pytest

from featurelifted import ConfigBox
from featurelifted.exceptions import BoxKeyError


def test_case_insensitive_key_lookup() -> None:
    cfg = ConfigBox(MY_FLAG="yes")
    assert cfg.bool("my_flag") is True


def test_list_with_mod_callback() -> None:
    cfg = ConfigBox(items="1, 2, 3")
    assert cfg.list("items", mod=lambda x: int(x.strip())) == [1, 2, 3]


def test_float_and_getfloat_default() -> None:
    cfg = ConfigBox(rate="2.5")
    assert cfg.float("rate") == 2.5
    assert cfg.getfloat("missing", 1.5) == 1.5


def test_getboolean_alias() -> None:
    cfg = ConfigBox(flag="false")
    assert cfg.getboolean("flag") is False


def test_missing_key_raises() -> None:
    cfg = ConfigBox()
    with pytest.raises(BoxKeyError):
        cfg.int("missing")


def test_no_box_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(r"^\\s*(?:from box|import box)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not import_pattern.search(path.read_text(encoding="utf-8"))
''')
    write_text(DESIGNS / f"{tid}.md", f"""# Task Design: `{tid}`

Status: draft

## Practical reuse

1. **Reuse module** — Typed config dict with dot access for twelve-factor apps and CLI defaults.
2. **Who imports it** — Teams using ConfigBox-style env/config parsing without file converters.
3. **Why not copy-all** — Full python-box bundles YAML/TOML converters, BoxList, and file loaders.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Case fold | `featurelifted/config_box.py` | `test_case_insensitive_key_lookup` |
| List mod | `featurelifted/config_box.py` | `test_list_with_mod_callback` |
| Box access | `featurelifted/box.py` | `test_dot_access` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""")
    write_text(SUBMISSIONS / tid / "naive/featurelifted/__init__.py", '''"""Naive ConfigBox dict wrapper."""

from __future__ import annotations

from typing import Any, Callable


class BoxKeyError(AttributeError):
    pass


class Box(dict):
    def __getattr__(self, item: str) -> Any:
        try:
            return self[item]
        except KeyError as exc:
            raise BoxKeyError(item) from exc


class ConfigBox(Box):
    def bool(self, item: str, default: Any = None) -> bool:
        value = self.get(item, default)
        if value is None:
            raise BoxKeyError(item)
        return str(value).lower() not in {"0", "false", "no", "n", "f"}

    def int(self, item: str, default: Any = None) -> int:
        value = self.get(item, default)
        if value is None:
            raise BoxKeyError(item)
        return int(value)

    def float(self, item: str, default: Any = None) -> float:
        value = self.get(item, default)
        if value is None:
            raise BoxKeyError(item)
        return float(value)

    def list(self, item: str, default: Any = None, mod: Callable[[str], Any] | None = None) -> list[Any]:
        value = self.get(item, default)
        if value is None:
            raise BoxKeyError(item)
        parts = [value] if not isinstance(value, str) else value.split(",")
        return [mod(p) if mod else p for p in parts]

    def getfloat(self, item: str, default: Any = None) -> float:
        return self.float(item, default)

    def getboolean(self, item: str, default: Any = None) -> bool:
        return self.bool(item, default)
''')


def scaffold_arrow() -> None:
    tid = "arrow__parse_format_core__001"
    task = STAGING / tid
    copy_pkg_py(SITE / "arrow", task / "repo" / "arrow")
    write_json(task / "metadata.json", {
        "task_id": tid,
        "language": "python",
        "difficulty": "hard",
        "tags": ["batch-1", "arrow", "datetime", "hard-first", "functional-discriminator", "parser_state_coupling"],
        "source": {"name": "arrow", "url": "https://github.com/arrow-py/arrow", "commit": "1.2.3-installed-snapshot", "license": "Apache-2.0"},
        "feature": {
            "name": "Arrow parse, format, and humanize subset",
            "description": "Extract Arrow parsing, strftime-style formatting, and English humanize without importing arrow.",
            "source_entrypoints": ["arrow.get", "arrow.Arrow.format", "arrow.Arrow.humanize", "arrow.parser.DateTimeParser"],
            "included_behaviors": ["parse ISO and format-string datetimes", "format with token literals in brackets", "humanize relative deltas in English", "ordinal Do token parsing"],
            "excluded_behaviors": ["60+ locale packs beyond English", "timezone name database beyond utc/fixed offsets", "factory range/span utilities and CLI", "original arrow import at runtime"],
        },
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "data_model_coupling", "implicit_dependency_coupling"],
            "primary": "parser_state_coupling",
            "description": "Arrow couples parser token tables, formatter locale lookups, and Arrow datetime humanize hooks.",
            "signals": ["parser handles ordinal and timezone tokens", "formatter escapes bracket literals", "humanize uses English locale frames", "factory normalizes whitespace in parse strings"],
        },
        "output": {
            "package": "featurelifted",
            "import": "import featurelifted; from featurelifted import Arrow, get",
            "callable": "featurelifted.get",
            "signature": "get(*args, **kwargs) -> Arrow",
        },
        "environment": {
            "python": "3.11", "network": False, "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": ["python-dateutil"],
            "forbidden_dependencies": ["arrow"], "forbidden_imports": ["arrow"],
        },
        "tests": {"public": "public_tests/", "hidden": "hidden_tests/", "command": "pytest"},
    })
    write_text(task / "evaluation/forbidden_imports.txt", "arrow\n")
    write_json(task / "evaluation/oracle_manifest.json", {
        "source_package_name": "arrow",
        "required_source_files": [
            "arrow/parser.py", "arrow/formatter.py", "arrow/arrow.py", "arrow/factory.py",
            "arrow/api.py", "arrow/constants.py", "arrow/util.py", "arrow/locales.py",
        ],
        "runtime_dependencies": ["python-dateutil"],
        "notes": "Oracle uses English-only trimmed locales; repo ships full locales.py for copy-all penalty.",
    })
    write_text(task / "requirements.lock", "")
    write_text(task / "public_tests/test_public_api.py", '''from __future__ import annotations

from featurelifted import get


def test_get_iso_datetime() -> None:
    a = get("2020-01-15T12:30:00+00:00")
    assert a.year == 2020
    assert a.month == 1
    assert a.day == 15
    assert a.hour == 12
    assert a.minute == 30


def test_format_basic_tokens() -> None:
    a = get("2020-01-15T12:30:00+00:00")
    assert a.format("YYYY-MM-DD HH:mm:ss ZZ") == "2020-01-15 12:30:00 +00:00"


def test_get_with_format_string() -> None:
    a = get("2020-01-15 12:30", "YYYY-MM-DD HH:mm")
    assert a.format("YYYY-MM-DD") == "2020-01-15"
''')
    write_text(task / "hidden_tests/test_hidden_behavior.py", '''from __future__ import annotations

import re
from pathlib import Path

from featurelifted import get


def test_format_literal_brackets() -> None:
    a = get("2020-01-15T12:30:00+00:00")
    assert a.format("YYYY [MM] DD") == "2020 MM 15"


def test_humanize_relative_hours() -> None:
    a = get("2020-01-15T12:30:00+00:00")
    other = get("2020-01-15T10:00:00+00:00")
    assert a.humanize(other) == "in 2 hours"


def test_parse_ordinal_day_token() -> None:
    a = get("January 5th 2020", "MMMM Do YYYY")
    assert a.year == 2020
    assert a.month == 1
    assert a.day == 5


def test_parse_lowercase_month() -> None:
    a = get("jan 15 2020", "MMM D YYYY")
    assert a.month == 1
    assert a.day == 15


def test_humanize_past_tense() -> None:
    a = get("2020-01-15T10:00:00+00:00")
    other = get("2020-01-15T12:30:00+00:00")
    assert a.humanize(other) == "2 hours ago"


def test_no_arrow_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(r"^\\s*(?:from arrow|import arrow)\\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not import_pattern.search(path.read_text(encoding="utf-8"))
''')
    write_text(DESIGNS / f"{tid}.md", f"""# Task Design: `{tid}`

Status: draft

## Practical reuse

1. **Reuse module** — Arrow-style datetime parse/format/humanize for APIs and logging.
2. **Who imports it** — Services needing Arrow ergonomics without 60+ locale files.
3. **Why not copy-all** — Full Arrow bundles locales.py (~6k LOC) and factory extras beyond English core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Parser ordinal | `featurelifted/parser.py` | `test_parse_ordinal_day_token` |
| Formatter literals | `featurelifted/formatter.py` | `test_format_literal_brackets` |
| English humanize | `featurelifted/locales.py` | `test_humanize_relative_hours` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""")
    write_text(SUBMISSIONS / tid / "naive/featurelifted/__init__.py", '''"""Shallow Arrow stub."""

from __future__ import annotations

from datetime import datetime, timezone


class Arrow(datetime):
    @classmethod
    def get(cls, value: str, fmt: str | None = None) -> "Arrow":
        if fmt is None:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            if fmt == "YYYY-MM-DD HH:mm":
                dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
            else:
                dt = datetime.strptime(value, "%Y-%m-%d")
            dt = dt.replace(tzinfo=timezone.utc)
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, tzinfo=dt.tzinfo)

    def format(self, fmt: str, locale: str | None = None) -> str:
        del locale
        mapping = {"YYYY": f"{self.year:04d}", "MM": f"{self.month:02d}", "DD": f"{self.day:02d}", "HH": f"{self.hour:02d}", "mm": f"{self.minute:02d}", "ss": f"{self.second:02d}", "ZZ": "+00:00"}
        out = fmt
        for token, repl in mapping.items():
            out = out.replace(token, repl)
        return out

    def humanize(self, other: "Arrow | None" = None, granularity: str = "auto", locale: str = "en") -> str:
        del granularity, locale
        if other is None:
            return "just now"
        delta = int((self - other).total_seconds())
        if delta > 0:
            return f"in {delta // 3600} hours"
        return f"{(-delta) // 3600} hours ago"


def get(*args, **kwargs) -> Arrow:
    del kwargs
    if len(args) == 1:
        return Arrow.get(str(args[0]))
    return Arrow.get(str(args[0]), str(args[1]))
''')


def main() -> None:
    for fn in (scaffold_humanize, scaffold_isodate, scaffold_rfc3986, scaffold_python_box, scaffold_arrow):
        fn()
        print(f"scaffolded {fn.__name__}")


if __name__ == "__main__":
    main()
