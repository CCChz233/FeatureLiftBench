import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Result:
    fixed: tuple
    named: dict
    def __getitem__(self, key):
        return self.named[key] if isinstance(key, str) else (tuple(self.fixed) + tuple(self.named.values()))[key]

_TYPE = {"d": (r"[-+]?\d+", int), "f": (r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", float), "w": (r"\w+", str), "": (r".+?", str)}
class Parser:
    def __init__(self, format, case_sensitive=False):
        self.format, self.case_sensitive = format, case_sensitive
        self.regex, self.fields = self._compile(format)
    def _compile(self, text):
        pattern, fields, index, pos = "", [], 0, 0
        while pos < len(text):
            if text.startswith("{{", pos): pattern += re.escape("{"); pos += 2; continue
            if text.startswith("}}", pos): pattern += re.escape("}"); pos += 2; continue
            if text[pos] != "{": pattern += re.escape(text[pos]); pos += 1; continue
            end = text.find("}", pos)
            if end < 0: raise ValueError("unmatched {")
            spec = text[pos + 1:end]
            if ":" in spec: name, kind = spec.split(":", 1)
            else: name, kind = spec, ""
            if kind not in _TYPE: raise ValueError(f"unknown format type {kind}")
            group = name or f"_fixed_{index}"
            if not name: index += 1
            pattern += f"(?P<{group}>{_TYPE[kind][0]})"
            fields.append((group, name, _TYPE[kind][1]))
            pos = end + 1
        flags = 0 if self.case_sensitive else re.IGNORECASE
        return re.compile("^" + pattern + "$", flags), fields
    def parse(self, string):
        match = self.regex.fullmatch(string)
        if not match: return None
        fixed, named = [], {}
        for group, name, convert in self.fields:
            value = convert(match.group(group))
            if name:
                named[name] = value
            else:
                fixed.append(value)
        return Result(tuple(fixed), named)
def compile(format, case_sensitive=False): return Parser(format, case_sensitive)
def parse(format, string, case_sensitive=False): return Parser(format, case_sensitive).parse(string)
