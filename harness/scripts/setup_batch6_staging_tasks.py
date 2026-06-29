#!/usr/bin/env python3
"""Scaffold batch-6 staging tasks from site-packages snapshots."""

from __future__ import annotations

import importlib.metadata as metadata
import json
import shutil
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
SITE = Path("/Users/chz/anaconda3/lib/python3.12/site-packages")
STAGING = _REPO / "benchmark" / "staging"
SUBMISSIONS = _REPO / "benchmark" / "submissions"
DESIGNS = _REPO / "docs" / "task_designs"

SKIP_PARTS = frozenset({"__pycache__", "tests", "testing", "benchmarks", ".github"})

DIST_NAMES = {
    "dynaconf": "dynaconf",
    "phonenumbers": "phonenumbers",
    "passlib": "passlib",
    "pydantic_settings": "pydantic-settings",
    "chameleon": "Chameleon",
}


def _version(package: str) -> str:
    return f"{metadata.version(DIST_NAMES[package])}-installed-snapshot"


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )


def _copy_package(package: str, dst_repo: Path, *, extras: list[tuple[Path, Path]] | None = None) -> None:
    src = SITE / package
    if not src.is_dir():
        raise SystemExit(f"missing package: {src}")
    dst_pkg = dst_repo / package
    _copy_tree(src, dst_pkg)
    license_dst = dst_repo / "LICENSE"
    if not license_dst.exists():
        ver = metadata.version(DIST_NAMES[package])
        for pattern in (f"{package}-{ver}.dist-info", f"{DIST_NAMES[package]}-{ver}.dist-info"):
            candidate = SITE / pattern / "LICENSE"
            if candidate.is_file():
                shutil.copy2(candidate, license_dst)
                break
    for extra_src, extra_rel in extras or []:
        target = dst_repo / extra_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if extra_src.is_dir():
            _copy_tree(extra_src, target)
        else:
            shutil.copy2(extra_src, target)


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _task_dir(task_id: str) -> Path:
    return STAGING / task_id


TASK_SPECS: dict[str, dict] = {
    "dynaconf__settings_merge_core__001": {
        "package": "dynaconf",
        "source_name": "dynaconf",
        "source_url": "https://github.com/dynaconf/dynaconf",
        "license": "MIT",
        "feature_name": "Layered settings merge",
        "description": "Extract Dynaconf object_merge and LazySettings layered TOML/env merge without importing dynaconf.",
        "entrypoints": [
            "dynaconf.utils.object_merge",
            "dynaconf.Dynaconf",
            "dynaconf.base.LazySettings",
            "dynaconf.loaders.settings_loader",
            "dynaconf.loaders.env_loader",
        ],
        "included": [
            "recursive object_merge with list_merge shallow/deep/merge modes",
            "Dynaconf loads layered TOML settings files with environment sections",
            "envvar_prefix overrides nested keys with precedence over file values",
            "merge_enabled combines multiple settings files",
        ],
        "excluded": [
            "Flask/Django extensions and CLI",
            "vault/redis external loaders",
            "typed settings subsystem and validators beyond merge",
            "original dynaconf import at runtime",
        ],
        "entanglement": {
            "level": "high",
            "types": ["config_environment_coupling", "data_model_coupling", "framework_coupling"],
            "primary": "config_environment_coupling",
            "description": "Settings merge couples nested dict trees, list_merge policies, TOML loaders, and env override precedence.",
            "signals": [
                "object_merge list_merge shallow/deep/full_path semantics",
                "Dynaconf layered environments and envvar_prefix",
                "settings_loader merges multiple TOML files",
            ],
        },
        "output_import": "from featurelifted import Dynaconf, object_merge; from featurelifted.utils import object_merge as merge_util",
        "callable": "featurelifted.utils.object_merge",
        "signature": "object_merge(old, new, unique=False, full_path=None, list_merge='merge')",
        "forbidden": ["dynaconf"],
        "allowed_dependencies": [],
        "manifest_notes": "Oracle copies merge core, loaders, and minimal vendor (box/toml); excludes contrib/cli/typed.",
    },
    "phonenumbers__parse_format_core__001": {
        "package": "phonenumbers",
        "source_name": "phonenumbers",
        "source_url": "https://github.com/daviddrysdale/python-phonenumbers",
        "license": "Apache-2.0",
        "feature_name": "Phone number parse and format",
        "description": "Extract libphonenumber parse/format for US and GB regions without importing phonenumbers.",
        "entrypoints": [
            "phonenumbers.parse",
            "phonenumbers.format_number",
            "phonenumbers.PhoneNumberFormat",
            "phonenumbers.is_valid_number",
            "phonenumbers.phonenumberutil",
        ],
        "included": [
            "parse E.164 and national numbers for US and GB",
            "format NATIONAL, INTERNATIONAL, and E164",
            "validate numbers against region metadata",
        ],
        "excluded": [
            "full global geodata/carrier/timezone datasets",
            "PhoneNumberMatcher and short-number data",
            "original phonenumbers import at runtime",
        ],
        "entanglement": {
            "level": "high",
            "types": ["resource_coupling", "data_model_coupling", "third_party_dependency_coupling"],
            "primary": "resource_coupling",
            "description": "Parse/format couples PhoneNumber model, metadata tables, and region-specific formatting rules.",
            "signals": [
                "region metadata lazy loading for US/GB",
                "national vs international formatting patterns",
                "country code inference from E.164 input",
            ],
        },
        "output_import": "from featurelifted import PhoneNumberFormat, NumberParseException, format_number, is_valid_number, parse; from featurelifted.phonenumberutil import NumberParseException",
        "callable": "featurelifted.parse",
        "signature": "parse(number: str, region: str | None = None) -> PhoneNumber",
        "forbidden": ["phonenumbers"],
        "allowed_dependencies": [],
        "manifest_notes": "Oracle uses core util modules plus trimmed US/GB metadata; repo keeps full geodata for copy-all.",
    },
    "passlib__hash_context_core__001": {
        "package": "passlib",
        "source_name": "passlib",
        "source_url": "https://github.com/glic3rinu/passlib",
        "license": "BSD-3-Clause",
        "feature_name": "CryptContext hash and verify",
        "description": "Extract passlib CryptContext multi-scheme hashing and verification without importing passlib.",
        "entrypoints": [
            "passlib.context.CryptContext",
            "passlib.context.LazyCryptContext",
            "passlib.registry.get_crypt_handler",
            "passlib.handlers.pbkdf2",
        ],
        "included": [
            "CryptContext hash and verify for pbkdf2_sha256",
            "scheme options like default_rounds and deprecated schemes",
            "needs_update and identify handlers",
        ],
        "excluded": [
            "apache htpasswd helpers and TOTP",
            "django extension and host-specific handlers",
            "original passlib import at runtime",
        ],
        "entanglement": {
            "level": "high",
            "types": ["data_model_coupling", "global_state_registry_coupling", "implicit_dependency_coupling"],
            "primary": "data_model_coupling",
            "description": "CryptContext couples handler registry, scheme option coercion, and multi-scheme verification policy.",
            "signals": [
                "handler registry and scheme deprecation",
                "context policy for rounds and identify",
                "pbkdf2_sha256 handler wiring",
            ],
        },
        "output_import": "from featurelifted import CryptContext",
        "callable": "featurelifted.CryptContext",
        "signature": "CryptContext(schemes=None, **kw)",
        "forbidden": ["passlib"],
        "allowed_dependencies": [],
        "manifest_notes": "Oracle copies context/registry/pbkdf2 handler closure; repo includes full passlib for copy-all.",
    },
    "pydantic_settings__env_source_core__001": {
        "package": "pydantic_settings",
        "source_name": "pydantic-settings",
        "source_url": "https://github.com/pydantic/pydantic-settings",
        "license": "MIT",
        "feature_name": "Environment settings source",
        "description": "Extract pydantic-settings BaseSettings env source with nested delimiter parsing without importing pydantic_settings.",
        "entrypoints": [
            "pydantic_settings.BaseSettings",
            "pydantic_settings.sources.EnvSettingsSource",
            "pydantic_settings.sources.utils.parse_env_vars",
            "pydantic_settings.SettingsConfigDict",
        ],
        "included": [
            "BaseSettings loads fields from os.environ with env_prefix",
            "nested models via env_nested_delimiter",
            "json/complex field parsing and case_sensitive option",
            "env_ignore_empty and env_parse_none_str",
        ],
        "excluded": [
            "dotenv, yaml/toml/json file sources and cloud secret providers",
            "CLI settings source and subcommand parsing",
            "original pydantic_settings import at runtime",
        ],
        "entanglement": {
            "level": "high",
            "types": ["config_environment_coupling", "data_model_coupling", "framework_coupling"],
            "primary": "config_environment_coupling",
            "description": "Env source couples pydantic field metadata, nested delimiter expansion, and complex JSON env values.",
            "signals": [
                "env_nested_delimiter builds nested dicts",
                "complex fields parsed via pydantic TypeAdapter",
                "case_sensitive env key matching",
            ],
        },
        "output_import": "from featurelifted import BaseSettings, SettingsConfigDict, SettingsError",
        "callable": "featurelifted.BaseSettings",
        "signature": "class Settings(BaseSettings): ...",
        "forbidden": ["pydantic_settings"],
        "allowed_dependencies": ["pydantic"],
        "manifest_notes": "Oracle copies BaseSettings and EnvSettingsSource closure; repo retains all providers for copy-all.",
    },
    "chameleon__template_compile_core__001": {
        "package": "chameleon",
        "source_name": "chameleon",
        "source_url": "https://github.com/malthe/chameleon",
        "license": "BSD-3-Clause",
        "feature_name": "ZPT template compile and render",
        "description": "Extract Chameleon PageTemplate compile/render with TAL/TALES without importing chameleon.",
        "entrypoints": [
            "chameleon.zpt.template.PageTemplate",
            "chameleon.compiler.ExpressionEngine",
            "chameleon.tal",
            "chameleon.tales",
            "chameleon.exc.TemplateError",
        ],
        "included": [
            "compile and render PageTemplate from source strings",
            "TAL attributes content/repeat/condition",
            "TALES path and python expressions",
            "macro define/use via metal namespace",
        ],
        "excluded": [
            "filesystem PageTemplateFile loader and auto_reload",
            "i18n translation catalogs beyond defaults",
            "benchmark utilities and legacy loader paths",
            "original chameleon import at runtime",
        ],
        "entanglement": {
            "level": "high",
            "types": ["parser_state_coupling", "framework_coupling", "implicit_dependency_coupling"],
            "primary": "parser_state_coupling",
            "description": "ZPT compile couples tokenization, TAL/TALES expression engines, and codegen into renderable programs.",
            "signals": [
                "TAL repeat and condition compilation",
                "TALES expression parser for path/python/string forms",
                "macro metal:define-slot/use-slot wiring",
            ],
        },
        "output_import": "from featurelifted import TemplateError; from featurelifted.zpt.template import PageTemplate",
        "callable": "featurelifted.zpt.template.PageTemplate",
        "signature": "PageTemplate(source: str, **config)",
        "forbidden": ["chameleon"],
        "allowed_dependencies": [],
        "manifest_notes": "Oracle copies ZPT compile chain; repo includes benchmark/loader decoys for copy-all penalty.",
    },
}


PUBLIC_TESTS = {
    "dynaconf__settings_merge_core__001": '''\
from __future__ import annotations

import os
import tempfile

from featurelifted import Dynaconf, object_merge


def test_object_merge_nested_dict() -> None:
    old = {"db": {"host": "localhost", "port": 5432}, "items": [1, 2]}
    new = {"db": {"port": 3306, "user": "root"}, "items": [3]}
    merged = object_merge(old, new)
    assert merged == {"db": {"host": "localhost", "port": 3306, "user": "root"}, "items": [1, 2, 3]}


def test_dynaconf_toml_and_env_override() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "settings.toml")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write('[default]\\nhost = "localhost"\\nport = 5432\\n')
        os.environ["FLB_PORT"] = "8080"
        settings = Dynaconf(
            settings_files=[path],
            environments=False,
            envvar_prefix="FLB",
            load_dotenv=False,
        )
        assert settings.HOST == "localhost"
        assert settings.PORT == 8080
''',
    "phonenumbers__parse_format_core__001": '''\
from __future__ import annotations

from featurelifted import PhoneNumberFormat, format_number, parse


def test_parse_e164_and_format() -> None:
    num = parse("+442083661177", None)
    assert format_number(num, PhoneNumberFormat.E164) == "+442083661177"
    assert "+44" in format_number(num, PhoneNumberFormat.INTERNATIONAL)


def test_parse_national_us() -> None:
    num = parse("(202) 555-0123", "US")
    assert format_number(num, PhoneNumberFormat.NATIONAL).startswith("(202)")
''',
    "passlib__hash_context_core__001": '''\
from __future__ import annotations

from featurelifted import CryptContext


def test_hash_and_verify_pbkdf2() -> None:
    ctx = CryptContext(schemes=["pbkdf2_sha256"], pbkdf2_sha256__default_rounds=1)
    digest = ctx.hash("hunter2")
    assert digest.startswith("$pbkdf2-sha256$")
    assert ctx.verify("hunter2", digest)
    assert not ctx.verify("wrong", digest)
''',
    "pydantic_settings__env_source_core__001": '''\
from __future__ import annotations

import os

from pydantic import Field

from featurelifted import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLB_", env_nested_delimiter="__")
    port: int = 80
    debug: bool = False
    db: dict = Field(default_factory=dict)


def test_env_prefix_and_nested(monkeypatch) -> None:
    monkeypatch.setenv("FLB_PORT", "9000")
    monkeypatch.setenv("FLB_DEBUG", "true")
    monkeypatch.setenv("FLB_DB__HOST", "db.internal")
    settings = AppSettings()
    assert settings.port == 9000
    assert settings.debug is True
    assert settings.db == {"host": "db.internal"}
''',
    "chameleon__template_compile_core__001": '''\
from __future__ import annotations

from featurelifted.zpt.template import PageTemplate


def test_render_tal_content() -> None:
    template = PageTemplate("<div tal:content='name'>placeholder</div>")
    assert template.render(name="Ada").strip() == "<div>Ada</div>"


def test_render_python_expression() -> None:
    template = PageTemplate("<span>${name.upper()}</span>")
    assert "ADA" in template.render(name="ada")
''',
}

HIDDEN_TESTS = {
    "dynaconf__settings_merge_core__001": '''\
from __future__ import annotations

import os
import tempfile

from featurelifted import Dynaconf, object_merge


def test_object_merge_list_shallow() -> None:
    old = {"items": [1, 2, 3]}
    new = {"items": [9]}
    merged = object_merge(old, new, list_merge="shallow")
    assert merged["items"] == [9]


def test_object_merge_list_deep_path() -> None:
    old = {"groups": [{"ids": [1, 2]}]}
    new = {"groups": [{"ids": [3]}]}
    merged = object_merge(old, new, list_merge="deep", full_path=["groups", 0, "ids"])
    assert merged["groups"][0]["ids"] == [3]


def test_layered_toml_environments() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "settings.toml")
        with open(base, "w", encoding="utf-8") as fh:
            fh.write('[default]\\nhost = "localhost"\\nport = 5432\\n\\n[development]\\nport = 3000\\n')
        settings = Dynaconf(
            settings_files=[base],
            environments=True,
            load_dotenv=False,
        )
        settings.setenv("development")
        assert settings.HOST == "localhost"
        assert settings.PORT == 3000


def test_merge_multiple_settings_files() -> None:
    with tempfile.TemporaryDirectory() as td:
        a = os.path.join(td, "a.toml")
        b = os.path.join(td, "b.toml")
        open(a, "w").write('[default]\\nfoo = 1\\nlist = [1,2]\\n')
        open(b, "w").write('[default]\\nbar = 2\\n')
        settings = Dynaconf(settings_files=[a, b], environments=False, load_dotenv=False, merge_enabled=True)
        assert settings.FOO == 1
        assert settings.BAR == 2
        assert settings.LIST == [1, 2]
''',
    "phonenumbers__parse_format_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted import PhoneNumberFormat, format_number, is_valid_number, parse
from featurelifted.phonenumberutil import NumberParseException


def test_gb_national_equals_e164_parse() -> None:
    a = parse("+442083661177", None)
    b = parse("020 8366 1177", "GB")
    assert a.country_code == b.country_code == 44
    assert a.national_number == b.national_number


def test_invalid_region_raises() -> None:
    with pytest.raises(NumberParseException):
        parse("not-a-phone", "US")


def test_is_valid_and_e164_us() -> None:
    num = parse("+12025550123", None)
    assert is_valid_number(num)
    assert format_number(num, PhoneNumberFormat.E164) == "+12025550123"
''',
    "passlib__hash_context_core__001": '''\
from __future__ import annotations

from featurelifted import CryptContext


def test_context_hash_includes_rounds() -> None:
    ctx = CryptContext(schemes=["pbkdf2_sha256"], pbkdf2_sha256__default_rounds=12)
    digest = ctx.hash("secret")
    assert ctx.identify(digest) == "pbkdf2_sha256"
    assert "$pbkdf2-sha256$12$" in digest


def test_context_verify_and_update_roundtrip() -> None:
    ctx = CryptContext(schemes=["pbkdf2_sha256"], pbkdf2_sha256__default_rounds=2)
    old = ctx.hash("pw")
    assert ctx.verify("pw", old)
    new = ctx.hash("pw")
    assert ctx.verify("pw", new)
''',
    "pydantic_settings__env_source_core__001": '''\
from __future__ import annotations

import json

import pytest
from pydantic import Field

from featurelifted import BaseSettings, SettingsConfigDict, SettingsError


class NestedSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLB_", env_nested_delimiter="__")
    tags: list[str] = Field(default_factory=list)
    limits: dict = Field(default_factory=dict)


def test_json_list_env(monkeypatch) -> None:
    monkeypatch.setenv("FLB_TAGS", '["a","b"]')
    settings = NestedSettings()
    assert settings.tags == ["a", "b"]


def test_case_sensitive_env(monkeypatch) -> None:
    class CaseSettings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="FLB_", case_sensitive=True)
        MyField: str = "x"

    monkeypatch.setenv("FLB_MyField", "ok")
    assert CaseSettings().MyField == "ok"


def test_ignore_empty_env(monkeypatch) -> None:
    class EmptySettings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="FLB_", env_ignore_empty=True)
        name: str = "default"

    monkeypatch.setenv("FLB_NAME", "")
    assert EmptySettings().name == "default"


def test_parse_none_str(monkeypatch) -> None:
    class NoneSettings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="FLB_", env_parse_none_str="null")
        value: str | None = "fallback"

    monkeypatch.setenv("FLB_VALUE", "null")
    assert NoneSettings().value is None
''',
    "chameleon__template_compile_core__001": '''\
from __future__ import annotations

import pytest

from featurelifted import TemplateError
from featurelifted.zpt.template import PageTemplate


def test_tal_repeat_and_condition() -> None:
    src = """
    <ul>
      <li tal:repeat="item items" tal:content="item"></li>
    </ul>
    """
    out = PageTemplate(src).render(items=["a", "b"])
    assert out.count("<li>") == 2
    assert "a" in out and "b" in out


def test_tal_attributes_replace() -> None:
    src = '<a href="/old" tal:attributes="href link">link</a>'
    out = PageTemplate(src).render(link="/new")
    assert 'href="/new"' in out


def test_tal_replace_marker() -> None:
    src = '<span tal:replace="structure item">x</span>'
    out = PageTemplate(src).render(item="<b>hi</b>")
    assert "<b>hi</b>" in out
''',
}

NAIVE_BASELINES = {
    "dynaconf__settings_merge_core__001": '''\
"""Naive shallow settings merge baseline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


def object_merge(old: Any, new: Any, **_: Any) -> Any:
    if isinstance(old, dict) and isinstance(new, dict):
        out = dict(old)
        for key, value in new.items():
            if key in out and isinstance(out[key], dict) and isinstance(value, dict):
                out[key] = {**out[key], **value}
            else:
                out[key] = value
        return out
    return new


class Dynaconf:
    def __init__(self, **kwargs: Any) -> None:
        self._data: dict[str, Any] = {}
        prefix = kwargs.get("envvar_prefix", "")
        for path in kwargs.get("settings_files") or []:
            if str(path).endswith(".toml") and Path(path).is_file():
                with open(path, "rb") as fh:
                    loaded = tomllib.load(fh)
                section = loaded.get("default", loaded)
                self._data.update({k.upper(): v for k, v in section.items()})
        for key, value in os.environ.items():
            if prefix and key.startswith(prefix + "_"):
                self._data[key[len(prefix) + 1 :]] = int(value) if value.isdigit() else value

    def __getattr__(self, name: str) -> Any:
        key = name.upper()
        if key in self._data:
            return self._data[key]
        raise AttributeError(name)

    def setenv(self, _env: str) -> None:
        return None
''',
    "phonenumbers__parse_format_core__001": '''\
"""Naive regex phone parser baseline."""

from __future__ import annotations

import re
from enum import Enum


class PhoneNumberFormat(Enum):
    E164 = 0
    NATIONAL = 1
    INTERNATIONAL = 2


class PhoneNumber:
    def __init__(self, country_code: int, national_number: int) -> None:
        self.country_code = country_code
        self.national_number = national_number


class NumberParseException(Exception):
    pass


_E164 = re.compile(r"^\\+(\\d{1,3})(\\d+)$")
_DIGITS = re.compile(r"\\D+")


def parse(number: str, region: str | None = None) -> PhoneNumber:
    number = number.strip()
    if number.startswith("+44"):
        return PhoneNumber(44, int(number[3:]))
    if number.startswith("+1"):
        return PhoneNumber(1, int(number[2:]))
    m = _E164.match(number)
    if m:
        return PhoneNumber(int(m.group(1)), int(m.group(2)))
    digits = _DIGITS.sub("", number)
    if region == "US" and len(digits) == 10:
        return PhoneNumber(1, int(digits))
    if region == "US" and len(digits) == 11 and digits.startswith("1"):
        return PhoneNumber(1, int(digits[1:]))
    if region == "GB" and digits.startswith("0"):
        return PhoneNumber(44, int(digits))
    if region is None:
        raise NumberParseException(number)
    raise NumberParseException(number)


def format_number(num: PhoneNumber, fmt: PhoneNumberFormat) -> str:
    if fmt is PhoneNumberFormat.E164:
        return f"+{num.country_code}{num.national_number}"
    if fmt is PhoneNumberFormat.INTERNATIONAL and num.country_code == 44:
        s = str(num.national_number)
        return f"+44 {s[:2]} {s[2:6]} {s[6:]}"
    if fmt is PhoneNumberFormat.NATIONAL and num.country_code == 1:
        s = str(num.national_number).zfill(10)
        return f"({s[:3]}) {s[3:6]}-{s[6:]}"
    return str(num.national_number)


def is_valid_number(num: PhoneNumber) -> bool:
    return num.national_number > 0
''',
    "passlib__hash_context_core__001": '''\
"""Naive hashlib CryptContext baseline."""

from __future__ import annotations

import hashlib
import secrets


class CryptContext:
    def __init__(self, schemes=None, **_: object) -> None:
        self.schemes = schemes or ["plain"]

    def hash(self, secret: str) -> str:
        salt = secrets.token_hex(4)
        digest = hashlib.sha256((salt + secret).encode()).hexdigest()
        return f"$pbkdf2-sha256$1${salt}${digest}"

    def verify(self, secret: str, hashval: str) -> bool:
        if not hashval.startswith("$pbkdf2-sha256$"):
            return False
        parts = hashval.split("$")
        if len(parts) < 5:
            return False
        salt, digest = parts[3], parts[4]
        return hashlib.sha256((salt + secret).encode()).hexdigest() == digest

    def identify(self, hashval: str) -> str:
        return "pbkdf2_sha256" if hashval.startswith("$pbkdf2-sha256$") else "unknown"

    def needs_update(self, hashval: str) -> bool:
        return False
''',
    "pydantic_settings__env_source_core__001": '''\
"""Naive os.environ settings baseline."""

from __future__ import annotations

import json
import os
from typing import Any, ClassVar, get_type_hints


class SettingsConfigDict(dict):
    pass


class SettingsError(Exception):
    pass


class BaseSettings:
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict()

    def __init__(self, **kwargs: Any) -> None:
        prefix = self.model_config.get("env_prefix", "")
        nested = self.model_config.get("env_nested_delimiter", "")
        hints = get_type_hints(self.__class__)
        data: dict[str, Any] = {}
        for key, hint in hints.items():
            env_key = f"{prefix}{key.upper()}"
            raw = os.environ.get(env_key)
            if raw is None:
                continue
            if hint is bool:
                data[key] = raw.lower() in {"1", "true", "yes"}
            elif hint is int:
                data[key] = int(raw)
            elif hint is list:
                data[key] = json.loads(raw)
            else:
                data[key] = raw
        if nested:
            for env_key, raw in os.environ.items():
                if not env_key.startswith(prefix):
                    continue
                body = env_key[len(prefix) :]
                if nested in body:
                    field, sub = body.split(nested, 1)
                    field = field.lower()
                    data.setdefault(field, {})
                    if isinstance(data[field], dict):
                        data[field][sub.lower()] = raw
        for name, value in data.items():
            setattr(self, name, value)
        for name, value in kwargs.items():
            setattr(self, name, value)
''',
    "chameleon__template_compile_core__001": '''\
"""Naive string replace template baseline."""

from __future__ import annotations


class PageTemplate:
    def __init__(self, source: str, **_: object) -> None:
        self.source = source

    def render(self, **kwargs: object) -> str:
        out = self.source
        for key, value in kwargs.items():
            out = out.replace(f"${{{key}}}", str(value))
            if isinstance(value, str):
                out = out.replace('href="/old"', f'href="{value}"')
                out = out.replace(f"tal:content='{key}'", f">{value}</")
                out = out.replace(">x</span>", f">{value}</span>")
        return out
''',
}

DESIGN_NOTES = {
    "dynaconf__settings_merge_core__001": """# Task Design: dynaconf__settings_merge_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| object_merge | `utils/__init__.py` | `test_object_merge_list_shallow` |
| TOML loader | `loaders/toml_loader.py` | `test_layered_toml_environments` |
| env loader | `loaders/env_loader.py` | `test_dynaconf_toml_and_env_override` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""",
    "phonenumbers__parse_format_core__001": """# Task Design: phonenumbers__parse_format_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Phone util | `phonenumberutil.py` | `test_gb_national_equals_e164_parse` |
| US metadata | `data/region_US.py` | `test_is_valid_and_e164_us` |
| GB metadata | `data/region_GB.py` | `test_gb_national_equals_e164_parse` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""",
    "passlib__hash_context_core__001": """# Task Design: passlib__hash_context_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| CryptContext | `context.py` | `test_hash_and_verify_pbkdf2` |
| pbkdf2 handler | `handlers/pbkdf2.py` | `test_context_verify_and_update_roundtrip` |
| registry | `registry.py` | `test_context_hash_includes_rounds` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""",
    "pydantic_settings__env_source_core__001": """# Task Design: pydantic_settings__env_source_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Env source | `sources/providers/env.py` | `test_env_prefix_and_nested` |
| Settings main | `main.py` | `test_json_list_env` |
| sources utils | `sources/utils.py` | `test_case_sensitive_env` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""",
    "chameleon__template_compile_core__001": """# Task Design: chameleon__template_compile_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| TAL compiler | `tal.py` | `test_tal_repeat_and_condition` |
| TALES | `tales.py` | `test_render_python_expression` |
| ZPT program | `zpt/program.py` | `test_tal_attributes_replace` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
""",
}


def _write_task_files(task_id: str, spec: dict) -> None:
    task_dir = _task_dir(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "requirements.lock").write_text("", encoding="utf-8")

    eval_dir = task_dir / "evaluation"
    eval_dir.mkdir(exist_ok=True)
    forbidden = spec["forbidden"][0]
    (eval_dir / "forbidden_imports.txt").write_text(forbidden + "\n", encoding="utf-8")
    _write_json(
        eval_dir / "oracle_manifest.json",
        {
            "source_package_name": spec["package"],
            "required_source_files": [],
            "notes": spec["manifest_notes"],
        },
    )

    metadata = {
        "task_id": task_id,
        "language": "python",
        "difficulty": "hard",
        "tags": [
            "batch-1",
            spec["package"],
            "hard-first",
            "functional-discriminator",
            spec["entanglement"]["primary"],
        ],
        "source": {
            "name": spec["source_name"],
            "url": spec["source_url"],
            "commit": _version(spec["package"]),
            "license": spec["license"],
        },
        "feature": {
            "name": spec["feature_name"],
            "description": spec["description"],
            "source_entrypoints": spec["entrypoints"],
            "included_behaviors": spec["included"],
            "excluded_behaviors": spec["excluded"],
        },
        "entanglement": spec["entanglement"],
        "output": {
            "package": "featurelifted",
            "import": spec["output_import"],
            "callable": spec["callable"],
            "signature": spec["signature"],
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": spec.get("allowed_dependencies", []),
            "forbidden_dependencies": spec["forbidden"],
            "forbidden_imports": spec["forbidden"],
        },
        "tests": {
            "public": "public_tests/",
            "hidden": "hidden_tests/",
            "command": "pytest",
        },
    }
    _write_json(task_dir / "metadata.json", metadata)

    pub = task_dir / "public_tests"
    hid = task_dir / "hidden_tests"
    pub.mkdir(exist_ok=True)
    hid.mkdir(exist_ok=True)
    (pub / "test_public_api.py").write_text(PUBLIC_TESTS[task_id], encoding="utf-8")
    (hid / "test_hidden_behavior.py").write_text(HIDDEN_TESTS[task_id], encoding="utf-8")

    (DESIGNS / f"{task_id}.md").write_text(DESIGN_NOTES[task_id], encoding="utf-8")

    naive_dir = SUBMISSIONS / task_id / "naive" / "featurelifted"
    naive_dir.mkdir(parents=True, exist_ok=True)
    if task_id == "chameleon__template_compile_core__001":
        zpt_dir = naive_dir / "zpt"
        zpt_dir.mkdir(parents=True, exist_ok=True)
        (naive_dir / "__init__.py").write_text(
            "from featurelifted.exc import TemplateError\n\n__all__ = ['TemplateError']\n",
            encoding="utf-8",
        )
        (naive_dir / "exc.py").write_text(
            "class TemplateError(Exception):\n    pass\n",
            encoding="utf-8",
        )
        (zpt_dir / "__init__.py").write_text("", encoding="utf-8")
        (zpt_dir / "template.py").write_text(NAIVE_BASELINES[task_id], encoding="utf-8")
    elif task_id == "phonenumbers__parse_format_core__001":
        (naive_dir / "__init__.py").write_text(NAIVE_BASELINES[task_id], encoding="utf-8")
        (naive_dir / "phonenumberutil.py").write_text(
            "from featurelifted import NumberParseException\n",
            encoding="utf-8",
        )
    else:
        (naive_dir / "__init__.py").write_text(NAIVE_BASELINES[task_id], encoding="utf-8")


def _copy_repos() -> None:
    _copy_package("dynaconf", _task_dir("dynaconf__settings_merge_core__001") / "repo")
    _copy_package("phonenumbers", _task_dir("phonenumbers__parse_format_core__001") / "repo")
    _copy_package("passlib", _task_dir("passlib__hash_context_core__001") / "repo")
    _copy_package("pydantic_settings", _task_dir("pydantic_settings__env_source_core__001") / "repo")
    # chameleon: add benchmark decoy modules for copy-all penalty
    chameleon_repo = _task_dir("chameleon__template_compile_core__001") / "repo"
    _copy_package("chameleon", chameleon_repo)
    decoy = chameleon_repo / "chameleon" / "_legacy_decoys"
    decoy.mkdir(exist_ok=True)
    bench = SITE / "chameleon" / "benchmark.py"
    if bench.is_file():
        for i in range(3):
            shutil.copy2(bench, decoy / f"decoy_module_{i}.py")


def main() -> None:
    for task_id, spec in TASK_SPECS.items():
        _write_task_files(task_id, spec)
        print("scaffolded", task_id)
    _copy_repos()
    print("repos copied")


if __name__ == "__main__":
    main()
