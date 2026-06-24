#!/usr/bin/env python3
"""Generate sources/vibe_app curated legacy app snapshot."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "benchmark" / "sources" / "vibe_app"


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


LICENSE = """MIT License

Copyright (c) 2026 FeatureLiftBench Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

FILES: dict[str, str] = {}


def add(rel: str, content: str) -> None:
    FILES[rel] = content


add(
    "LICENSE",
    LICENSE,
)

add(
    "README.md",
    """# VibeShop (vibe_app)

Curated legacy-style Python shop backend for FeatureLiftBench.

Intentionally entangled: global state, YAML config side effects, duplicate helpers,
and a CSV pipeline spread across modules. Not intended for production use.
""",
)

add(
    "requirements.txt",
    """# Optional: PyYAML>=6.0,<7 for non-benchmark deployments.
""",
)

add(
    "setup.py",
    """from setuptools import find_packages, setup

setup(
    name="vibe_app",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
)
""",
)

add(
    "run.py",
    """#!/usr/bin/env python3
\"\"\"Legacy entrypoint — mostly unused in benchmark tasks.\"\"\"

from vibe_app.app import create_app
from vibe_app.config_loader import bootstrap_config

if __name__ == "__main__":
    bootstrap_config("config")
    app = create_app()
    print("VibeShop stub ready", app.name)
""",
)

add(
    "config/default.yaml",
    """app:
  name: VibeShop
  debug: false
  currency: USD
features:
  pricing_v2: true
  csv_import: true
logging:
  level: INFO
""",
)

add(
    "config/app.yaml",
    """app:
  debug: true
features:
  legacy_reports: false
""",
)

add(
    "config/pricing.yaml",
    """pricing:
  round_digits: 2
  categories:
    electronics: 1.05
    books: 0.95
    grocery: 1.00
    default: 1.0
  members:
    discount: 0.90
""",
)

add(
    "config/tiers.yaml",
    """pricing:
  tiers:
    - min_qty: 5
      multiplier: 0.98
    - min_qty: 10
      multiplier: 0.95
    - min_qty: 50
      multiplier: 0.90
""",
)

add(
    "data/sample_products.csv",
    """SKU,Name,Quantity,Category,Unit_Price
A100,Widget,12,electronics,9.99
B200,Notebook,3,books,4.50
C300,Rice,60,grocery,2.10
D400,Gadget,8,electronics,15.00
""",
)

add(
    "data/sample_orders.csv",
    """sku,name,quantity,category,unit_price
x1,Alpha,2,books,5.00
x2,Beta,15,electronics,3.25
x3,Gamma,0,grocery,1.00
""",
)

add(
    "vibe_app/__init__.py",
    """\"\"\"VibeShop package — intentionally cluttered.\"\"\"

__version__ = "0.0.1"
""",
)

add(
    "vibe_app/state.py",
    """\"\"\"Process-wide mutable registry used throughout the app.\"\"\"

from __future__ import annotations

from typing import Any

GLOBAL_STATE: dict[str, Any] = {
    "bootstrapped": False,
    "config": {},
    "config_paths": [],
    "load_count": 0,
    "feature_flags": {},
    "last_csv_job": None,
}


def reset_state() -> None:
    \"\"\"Testing helper — not part of benchmark APIs.\"\"\"
    GLOBAL_STATE.clear()
    GLOBAL_STATE.update(
        {
            "bootstrapped": False,
            "config": {},
            "config_paths": [],
            "load_count": 0,
            "feature_flags": {},
            "last_csv_job": None,
        }
    )


def touch(key: str, value: Any = True) -> None:
    GLOBAL_STATE.setdefault("touches", []).append((key, value))
""",
)

add(
    "vibe_app/yaml_compat.py",
    """\"\"\"Minimal YAML subset loader for simple config files (no PyYAML required).\"\"\"

from __future__ import annotations

from typing import Any


def safe_load(text: str) -> Any:
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith("#")):
        lines.pop(0)
    if not lines:
        return {}
    value, _ = _parse_value(lines, 0, _indent(lines[0]))
    return value


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_value(lines: list[str], index: int, indent: int) -> tuple[Any, int]:
    line = lines[index]
    stripped = line.strip()
    if stripped.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_mapping(lines, index, indent)


def _parse_mapping(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if _indent(line) < indent:
            break
        if _indent(line) > indent:
            break
        if line.strip().startswith("- "):
            break
        key, rest = _split_key_value(line.strip())
        index += 1
        if rest is not None:
            mapping[key] = _parse_scalar(rest)
            continue
        if index >= len(lines) or _indent(lines[index]) <= indent:
            mapping[key] = {}
            continue
        child, index = _parse_value(lines, index, _indent(lines[index]))
        mapping[key] = child
    return mapping, index


def _parse_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if _indent(line) < indent or not line.strip().startswith("- "):
            break
        payload = line.strip()[2:].strip()
        index += 1
        if payload:
            if ":" in payload:
                key, rest = _split_key_value(payload)
                item: dict[str, Any] = {key: _parse_scalar(rest) if rest is not None else {}}
                while index < len(lines) and _indent(lines[index]) > indent:
                    subline = lines[index]
                    if subline.strip().startswith("- "):
                        break
                    sub_key, sub_rest = _split_key_value(subline.strip())
                    index += 1
                    if sub_rest is not None:
                        item[sub_key] = _parse_scalar(sub_rest)
                    elif index < len(lines) and _indent(lines[index]) > _indent(subline):
                        nested, index = _parse_value(lines, index, _indent(lines[index]))
                        item[sub_key] = nested
                    else:
                        item[sub_key] = {}
                items.append(item)
            else:
                items.append(_parse_scalar(payload))
            continue
        if index < len(lines) and _indent(lines[index]) > indent:
            child, index = _parse_value(lines, index, _indent(lines[index]))
            items.append(child)
        else:
            items.append({})
    return items, index


def _split_key_value(text: str) -> tuple[str, str | None]:
    key, sep, rest = text.partition(":")
    if not sep:
        return text, None
    rest = rest.strip()
    return key.strip(), rest if rest else None


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
""",
)

add(
    "vibe_app/config_merge.py",
    """\"\"\"Deep merge helpers for layered YAML config.\"\"\"

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def merge_config_layers(*layers: dict[str, Any]) -> dict[str, Any]:
    \"\"\"Deep-merge config dicts; later layers override earlier keys.\"\"\"
    result: dict[str, Any] = {}
    for layer in layers:
        if not layer:
            continue
        result = _deep_merge(result, layer)
    return result


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in overlay.items():
        if key in merged and _is_mapping(merged[key]) and _is_mapping(value):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def merge_config_layers_shallow(*layers: dict[str, Any]) -> dict[str, Any]:
    \"\"\"Legacy shallow merge — wrong for nested overrides.\"\"\"
    result: dict[str, Any] = {}
    for layer in layers:
        result.update(layer)
    return result
""",
)

add(
    "vibe_app/config_loader.py",
    """\"\"\"YAML loading with registry side effects.\"\"\"

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from vibe_app.yaml_compat import safe_load as yaml_safe_load
from vibe_app.config_merge import merge_config_layers
from vibe_app.state import GLOBAL_STATE, touch

_ENV_PATTERN = re.compile(r"\\$\\{([^}:]+)(?::-(.*?))?\\}")


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            name = match.group(1)
            default = match.group(2)
            found = os.environ.get(name)
            if found is not None:
                return found
            if default is not None:
                return default
            return match.group(0)

        return _ENV_PATTERN.sub(repl, value)
    if isinstance(value, list):
        return [_expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand_env(item) for key, item in value.items()}
    return value


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    \"\"\"Load one YAML file and record the path in GLOBAL_STATE.\"\"\"
    resolved = Path(path)
    text = resolved.read_text(encoding="utf-8")
    data = yaml_safe_load(text) or {}
    data = _expand_env(data)
    GLOBAL_STATE["config_paths"].append(str(resolved))
    GLOBAL_STATE["load_count"] = int(GLOBAL_STATE.get("load_count", 0)) + 1
    touch("yaml_loaded", str(resolved))
    return data


def bootstrap_config(config_dir: str | Path) -> dict[str, Any]:
    \"\"\"Load default/app/pricing/tiers layers and store merged config.\"\"\"
    base = Path(config_dir)
    layer_names = ["default.yaml", "app.yaml", "pricing.yaml", "tiers.yaml"]
    layers = [load_yaml_config(base / name) for name in layer_names]
    merged = merge_config_layers(*layers)
    GLOBAL_STATE["config"] = merged
    GLOBAL_STATE["bootstrapped"] = True
    GLOBAL_STATE["feature_flags"] = dict(merged.get("features", {}))
    return merged


def bootstrap_config_fast(config_dir: str | Path) -> dict[str, Any]:
    \"\"\"Broken bootstrap — only reads default.yaml.\"\"\"
    base = Path(config_dir)
    data = load_yaml_config(base / "default.yaml")
    GLOBAL_STATE["config"] = data
    return data
""",
)

add(
    "vibe_app/helpers/__init__.py",
    '"""Helper subpackage."""\n',
)

add(
    "vibe_app/helpers/money.py",
    """\"\"\"Currency helpers.\"\"\"

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def round_money(value: float, digits: int = 2) -> float:
    quant = Decimal("1").scaleb(-digits)
    return float(Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP))


def format_money(value: float, currency: str = "USD") -> str:
    return f"{currency} {round_money(value):.2f}"
""",
)

add(
    "vibe_app/helpers/dates.py",
    """\"\"\"Date clutter — unused by benchmark features.\"\"\"

from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
""",
)

add(
    "vibe_app/helpers/strings.py",
    """\"\"\"String helpers duplicated elsewhere.\"\"\"

from __future__ import annotations


def slugify(value: str) -> str:
    return "-".join(part for part in value.lower().replace("_", " ").split() if part)


def normalize_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_")
""",
)

add(
    "vibe_app/pricing/__init__.py",
    """from vibe_app.pricing.rules import PricingContext, compute_line_price

__all__ = ["PricingContext", "compute_line_price"]
""",
)

add(
    "vibe_app/pricing/discounts.py",
    """\"\"\"Category and membership adjustments.\"\"\"

from __future__ import annotations

from typing import Any


def category_multiplier(category: str, pricing_cfg: dict[str, Any]) -> float:
    categories = pricing_cfg.get("categories", {})
    return float(categories.get(category, categories.get("default", 1.0)))


def member_multiplier(is_member: bool, pricing_cfg: dict[str, Any]) -> float:
    if not is_member:
        return 1.0
    members = pricing_cfg.get("members", {})
    return float(members.get("discount", 1.0))
""",
)

add(
    "vibe_app/pricing/tiers.py",
    """\"\"\"Quantity tier lookup.\"\"\"

from __future__ import annotations

from typing import Any


def tier_multiplier(quantity: int, tiers: list[dict[str, Any]]) -> float:
    applicable = 1.0
    for tier in sorted(tiers, key=lambda item: int(item.get("min_qty", 0))):
        min_qty = int(tier.get("min_qty", 0))
        if quantity >= min_qty:
            applicable = float(tier.get("multiplier", 1.0))
    return applicable
""",
)

add(
    "vibe_app/pricing/rules.py",
    """\"\"\"Canonical pricing rules engine.\"\"\"

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vibe_app.helpers.money import round_money
from vibe_app.pricing.discounts import category_multiplier, member_multiplier
from vibe_app.pricing.tiers import tier_multiplier
from vibe_app.state import GLOBAL_STATE


@dataclass
class PricingContext:
    is_member: bool = False
    customer_tier: str | None = None
    config: dict[str, Any] | None = None

    def pricing_section(self) -> dict[str, Any]:
        cfg = self.config or GLOBAL_STATE.get("config", {})
        return cfg.get("pricing", {})


def compute_line_price(
    unit_price: float,
    quantity: int,
    category: str,
    *,
    context: PricingContext | None = None,
) -> float:
    ctx = context or PricingContext()
    pricing_cfg = ctx.pricing_section()
    digits = int(pricing_cfg.get("round_digits", 2))

    subtotal = float(unit_price) * int(quantity)
    subtotal *= category_multiplier(category, pricing_cfg)
    subtotal *= tier_multiplier(int(quantity), list(pricing_cfg.get("tiers", [])))
    subtotal *= member_multiplier(ctx.is_member, pricing_cfg)
    return round_money(subtotal, digits)
""",
)

add(
    "vibe_app/pricing/legacy_pricing.py",
    """\"\"\"Old pricing path kept for backwards compat — wrong semantics.\"\"\"

from __future__ import annotations


def legacy_line_total(unit_price: float, quantity: int) -> float:
    return round(unit_price * quantity, 3)
""",
)

add(
    "vibe_app/utils.py",
    """\"\"\"Grab-bag utilities — three similar pricing helpers, only one is correct.\"\"\"

from __future__ import annotations

from vibe_app.pricing.legacy_pricing import legacy_line_total
from vibe_app.pricing.rules import PricingContext, compute_line_price

# re-export correct API for routes
__all__ = ["calc_price_v1", "calc_price_legacy", "compute_line_price", "PricingContext"]


def calc_price_v1(unit_price: float, quantity: int, category: str) -> float:
    \"\"\"WRONG: ignores category tiers and membership.\"\"\"
    _ = category
    return round(unit_price * quantity, 2)


def calc_price_legacy(unit_price: float, quantity: int, category: str) -> float:
    \"\"\"WRONG: uses legacy rounding and ignores category rules.\"\"\"
    _ = category
    return legacy_line_total(unit_price, quantity)


# compute_line_price imported from pricing.rules — canonical
""",
)

add(
    "vibe_app/csv_transform/schema.py",
    """\"\"\"CSV column schema hints.\"\"\"

REQUIRED_FIELDS = ("sku", "name", "quantity", "category", "unit_price")
OPTIONAL_FIELDS = ("notes", "warehouse")
""",
)

add(
    "vibe_app/csv_transform/reader.py",
    """\"\"\"CSV reader stage.\"\"\"

from __future__ import annotations

import csv
import io
from typing import Any


def read_csv_rows(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]
""",
)

add(
    "vibe_app/csv_transform/mapper.py",
    """\"\"\"Header and field normalization.\"\"\"

from __future__ import annotations

from typing import Any

from vibe_app.helpers.strings import normalize_header


def normalize_row_keys(row: dict[str, Any]) -> dict[str, Any]:
    return {normalize_header(str(key)): value for key, value in row.items()}


def coerce_numeric_fields(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)
    if "quantity" in result:
        result["quantity"] = int(str(result["quantity"]).strip() or "0")
    if "unit_price" in result:
        result["unit_price"] = float(str(result["unit_price"]).strip() or "0")
    return result
""",
)

add(
    "vibe_app/csv_transform/cleaner.py",
    """\"\"\"Row filtering helpers.\"\"\"

from __future__ import annotations

from typing import Any


def row_is_valid(row: dict[str, Any]) -> bool:
    sku = str(row.get("sku", "")).strip()
    qty = row.get("quantity", 0)
    try:
        qty_val = int(qty)
    except (TypeError, ValueError):
        return False
    return bool(sku) and qty_val > 0


def filter_by_min_quantity(row: dict[str, Any], minimum: int) -> bool:
    try:
        return int(row.get("quantity", 0)) >= minimum
    except (TypeError, ValueError):
        return False
""",
)

add(
    "vibe_app/csv_transform/transforms/normalize.py",
    """from vibe_app.csv_transform.mapper import coerce_numeric_fields, normalize_row_keys


def normalize_record(row: dict) -> dict:
    return coerce_numeric_fields(normalize_row_keys(row))
""",
)

add(
    "vibe_app/csv_transform/transforms/filter_rows.py",
    """from vibe_app.csv_transform.cleaner import filter_by_min_quantity, row_is_valid


def filter_records(rows: list[dict], *, min_quantity: int = 0) -> list[dict]:
    kept: list[dict] = []
    for row in rows:
        if not row_is_valid(row):
            continue
        if min_quantity and not filter_by_min_quantity(row, min_quantity):
            continue
        kept.append(row)
    return kept
""",
)

add(
    "vibe_app/csv_transform/transforms/aggregate.py",
    """\"\"\"Optional grouping stage.\"\"\"

from __future__ import annotations

from typing import Any


def aggregate_by(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for row in rows:
        group = str(row.get(key, ""))
        if group not in buckets:
            buckets[group] = {key: group, "quantity": 0, "unit_price": 0.0, "rows": 0}
        bucket = buckets[group]
        bucket["quantity"] += int(row.get("quantity", 0))
        bucket["unit_price"] += float(row.get("unit_price", 0.0))
        bucket["rows"] += 1
    return sorted(buckets.values(), key=lambda item: str(item.get(key, "")))
""",
)

add(
    "vibe_app/csv_transform/transforms/dedupe.py",
    """\"\"\"Dedupe by sku — last row wins.\"\"\"

from __future__ import annotations

from typing import Any


def dedupe_by_sku(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        seen[str(row.get("sku", ""))] = row
    return [seen[key] for key in sorted(seen)]
""",
)

add(
    "vibe_app/csv_transform/transforms/__init__.py",
    """from vibe_app.csv_transform.transforms.aggregate import aggregate_by
from vibe_app.csv_transform.transforms.dedupe import dedupe_by_sku
from vibe_app.csv_transform.transforms.filter_rows import filter_records
from vibe_app.csv_transform.transforms.normalize import normalize_record

__all__ = ["aggregate_by", "dedupe_by_sku", "filter_records", "normalize_record"]
""",
)

add(
    "vibe_app/csv_transform/writer.py",
    """\"\"\"Serialize rows back to CSV — mostly unused in tasks.\"\"\"

from __future__ import annotations

import csv
import io
from typing import Any


def rows_to_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    fieldnames = sorted({key for row in rows for key in row})
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()
""",
)

add(
    "vibe_app/csv_transform/pipeline.py",
    """\"\"\"CSV transform pipeline orchestrator.\"\"\"

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vibe_app.csv_transform.reader import read_csv_rows
from vibe_app.csv_transform.transforms import (
    aggregate_by,
    dedupe_by_sku,
    filter_records,
    normalize_record,
)
from vibe_app.state import GLOBAL_STATE


@dataclass
class TransformOptions:
    group_by: str | None = None
    min_quantity: int = 0
    dedupe: bool = True


def transform_csv(csv_text: str, *, options: TransformOptions | None = None) -> list[dict[str, Any]]:
    opts = options or TransformOptions()
    rows = read_csv_rows(csv_text)
    normalized = [normalize_record(row) for row in rows]
    filtered = filter_records(normalized, min_quantity=opts.min_quantity)
    if opts.dedupe:
        filtered = dedupe_by_sku(filtered)
    if opts.group_by:
        filtered = aggregate_by(filtered, opts.group_by)
    else:
        filtered = sorted(filtered, key=lambda row: str(row.get("sku", "")))
    GLOBAL_STATE["last_csv_job"] = {"rows": len(filtered), "group_by": opts.group_by}
    return filtered
""",
)

add(
    "vibe_app/csv_transform/__init__.py",
    """from vibe_app.csv_transform.pipeline import TransformOptions, transform_csv

__all__ = ["TransformOptions", "transform_csv"]
""",
)

add(
    "vibe_app/models/product.py",
    """\"\"\"Product model clutter.\"\"\"

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Product:
    sku: str
    name: str
    category: str
    unit_price: float
""",
)

add(
    "vibe_app/models/order.py",
    """\"\"\"Order model clutter.\"\"\"

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OrderLine:
    sku: str
    quantity: int
    category: str
    unit_price: float


@dataclass
class Order:
    lines: list[OrderLine] = field(default_factory=list)
""",
)

add(
    "vibe_app/services/catalog_service.py",
    """\"\"\"Catalog lookups — not needed for benchmark APIs.\"\"\"

from __future__ import annotations

from vibe_app.models.product import Product


def sample_catalog() -> list[Product]:
    return [
        Product("A100", "Widget", "electronics", 9.99),
        Product("B200", "Notebook", "books", 4.50),
    ]
""",
)

add(
    "vibe_app/services/order_service.py",
    """\"\"\"Order totals using pricing rules via utils indirection.\"\"\"

from __future__ import annotations

from vibe_app.pricing.rules import PricingContext
from vibe_app.utils import compute_line_price


def order_line_total(unit_price: float, quantity: int, category: str, *, member: bool = False) -> float:
    ctx = PricingContext(is_member=member)
    return compute_line_price(unit_price, quantity, category, context=ctx)
""",
)

add(
    "vibe_app/services/report_service.py",
    """\"\"\"Reporting clutter using wrong pricing helper.\"\"\"

from __future__ import annotations

from vibe_app.utils import calc_price_v1


def quick_report_total(unit_price: float, quantity: int, category: str) -> float:
    return calc_price_v1(unit_price, quantity, category)
""",
)

add(
    "vibe_app/middleware/auth_stub.py",
    """\"\"\"Unused auth stub.\"\"\"

from vibe_app.state import GLOBAL_STATE


def fake_auth(token: str | None) -> bool:
    GLOBAL_STATE.setdefault("auth_checks", 0)
    GLOBAL_STATE["auth_checks"] += 1
    return bool(token)
""",
)

add(
    "vibe_app/middleware/logging_middleware.py",
    """\"\"\"Logging stub.\"\"\"

import logging

logger = logging.getLogger("vibeshop")


def log_request(path: str) -> None:
    logger.info("request %s", path)
""",
)

add(
    "vibe_app/routes.py",
    """\"\"\"Flask-ish routes — framework coupling clutter.\"\"\"

from __future__ import annotations

from vibe_app.config_loader import bootstrap_config
from vibe_app.csv_transform.pipeline import TransformOptions, transform_csv
from vibe_app.services.order_service import order_line_total
from vibe_app.utils import calc_price_legacy, calc_price_v1, compute_line_price


class FakeRequest:
    def __init__(self, json: dict | None = None):
        self.json = json or {}


class FakeApp:
    def __init__(self, name: str):
        self.name = name
        self._routes: dict[str, object] = {}

    def route(self, path: str):
        def decorator(func):
            self._routes[path] = func
            return func

        return decorator


def register_routes(app: FakeApp) -> None:
    @app.route("/health")
    def health():
        return {"ok": True}

    @app.route("/price")
    def price(request: FakeRequest | None = None):
        payload = (request or FakeRequest()).json
        # legacy path still wired for old clients
        if payload.get("legacy"):
            return {"total": calc_price_legacy(payload["unit_price"], payload["quantity"], payload["category"])}
        if payload.get("v1"):
            return {"total": calc_price_v1(payload["unit_price"], payload["quantity"], payload["category"])}
        return {
            "total": compute_line_price(
                payload["unit_price"],
                payload["quantity"],
                payload["category"],
            )
        }

    @app.route("/csv")
    def csv_route(request: FakeRequest | None = None):
        payload = (request or FakeRequest()).json
        opts = TransformOptions(min_quantity=int(payload.get("min_quantity", 0)))
        return {"rows": transform_csv(payload["csv"], options=opts)}

    @app.route("/bootstrap")
    def bootstrap_route(request: FakeRequest | None = None):
        payload = (request or FakeRequest()).json
        return bootstrap_config(payload.get("config_dir", "config"))
""",
)

add(
    "vibe_app/app.py",
    """\"\"\"Application factory with lazy imports and global bootstrap.\"\"\"

from __future__ import annotations

from vibe_app.routes import FakeApp, register_routes
from vibe_app.state import GLOBAL_STATE


def create_app(config_dir: str = "config") -> FakeApp:
    if not GLOBAL_STATE.get("bootstrapped"):
        from vibe_app.config_loader import bootstrap_config

        bootstrap_config(config_dir)
    app = FakeApp("vibeshop")
    register_routes(app)
    return app
""",
)


def pad_with_clutter() -> None:
    """Add near-duplicate helper modules to reach target LOC."""
    for idx in range(1, 12):
        add(
            f"vibe_app/clutter/legacy_helpers_{idx:02d}.py",
            f'''"""Auto-generated legacy helper module {idx} — noise for agents."""

from __future__ import annotations

from vibe_app.helpers.strings import normalize_header


def helper_{idx}(value: str) -> str:
    return normalize_header(value) + "-{idx}"


def duplicate_normalize(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def unused_total(values: list[float]) -> float:
    return sum(values) * {idx} / {idx + 1}
''',
        )
    add(
        "vibe_app/clutter/__init__.py",
        '"""Legacy clutter package."""\n',
    )


def main() -> None:
    pad_with_clutter()
    for rel, content in FILES.items():
        write(rel, content)
    py_files = list(ROOT.rglob("*.py"))
    loc = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in py_files)
    print(f"Wrote {len(py_files)} Python files, ~{loc} LOC under {ROOT}")


if __name__ == "__main__":
    main()
