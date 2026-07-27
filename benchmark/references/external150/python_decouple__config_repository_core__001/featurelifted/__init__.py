import os, re
_UNDEFINED = object()
class UndefinedValueError(ValueError): pass
class RepositoryDict:
    def __init__(self, data): self.data = dict(data)
    def __contains__(self, key): return key in self.data
    def __getitem__(self, key): return self.data[key]
class RepositoryEnv(RepositoryDict):
    def __init__(self, source):
        data = {}
        for raw in open(source, encoding="utf-8"):
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            key, value = line.split("=", 1); value = value.strip()
            if value[:1] in {"'", '"'}:
                quote = value[0]; end = value.find(quote, 1)
                value = value[1:end] if end >= 0 else value[1:]
            else: value = re.split(r"\s+#", value, 1)[0].strip()
            data[key.strip()] = value
        super().__init__(data)
class Csv:
    def __init__(self, cast=str, delimiter=",", strip=" "): self.cast, self.delimiter, self.strip = cast, delimiter, strip
    def __call__(self, value): return [self.cast(item.strip(self.strip)) for item in value.split(self.delimiter) if item.strip(self.strip)]
class Choices:
    def __init__(self, choices, cast=str): self.choices, self.cast = tuple(choices), cast
    def __call__(self, value):
        result = self.cast(value)
        if result not in self.choices: raise ValueError(f"{result!r} not in {self.choices!r}")
        return result
def _cast_bool(value):
    lowered = str(value).strip().lower()
    if lowered in {"true", "1", "yes", "y", "on"}: return True
    if lowered in {"false", "0", "no", "n", "off"}: return False
    raise ValueError(f"invalid boolean: {value}")
class Config:
    def __init__(self, repository, environ=None): self.repository, self.environ = repository, os.environ if environ is None else environ
    def __call__(self, option, default=_UNDEFINED, cast=_UNDEFINED):
        if option in self.environ: value = self.environ[option]
        elif option in self.repository: value = self.repository[option]
        elif default is not _UNDEFINED: value = default
        else: raise UndefinedValueError(f"{option} not found")
        if cast is _UNDEFINED: return value
        if cast is bool: return _cast_bool(value)
        return cast(value)
