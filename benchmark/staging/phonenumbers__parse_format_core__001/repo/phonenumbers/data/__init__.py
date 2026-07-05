"""Trimmed region metadata for US and GB."""

from ..phonemetadata import PhoneMetadata

_AVAILABLE_REGION_CODES = ["GB", "US"]
_AVAILABLE_NONGEO_COUNTRY_CODES: list[int] = []


def _load_region(code):
    __import__("region_%s" % code, globals(), locals(), fromlist=["PHONE_METADATA_%s" % code], level=1)


for _region_code in _AVAILABLE_REGION_CODES:
    PhoneMetadata.register_region_loader(_region_code, _load_region)

from .alt_format_44 import PHONE_ALT_FORMAT_44

_ALT_NUMBER_FORMATS = {44: PHONE_ALT_FORMAT_44}

_COUNTRY_CODE_TO_REGION_CODE = {1: ("US",), 44: ("GB",)}
