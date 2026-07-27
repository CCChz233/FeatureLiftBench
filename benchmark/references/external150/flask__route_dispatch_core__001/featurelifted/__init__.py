import re
from dataclasses import dataclass, field

@dataclass(eq=True)
class Response:
    body: object
    status_code: int = 200
    headers: dict = field(default_factory=dict)

class App:
    def __init__(self, name):
        self.name, self._routes, self._errors = name, [], {}
    def route(self, rule, methods=None):
        methods = tuple(m.upper() for m in (methods or ("GET",)))
        def register(func):
            names = []
            pattern = ""
            for part in re.split(r"(<[^>]+>)", rule):
                if part.startswith("<") and part.endswith(">"):
                    spec = part[1:-1]
                    if ":" in spec: kind, name = spec.split(":", 1)
                    else: kind, name = "string", spec
                    names.append((name, kind))
                    pattern += rf"(?P<{name}>\d+)" if kind == "int" else rf"(?P<{name}>[^/]+)"
                else: pattern += re.escape(part)
            self._routes.append((re.compile("^" + pattern + "$"), names, methods, func))
            return func
        return register
    def errorhandler(self, code):
        def register(func): self._errors[int(code)] = func; return func
        return register
    def _response(self, value):
        if isinstance(value, Response): return value
        if not isinstance(value, tuple): return Response(value)
        if len(value) == 2: return Response(value[0], value[1])
        return Response(value[0], value[1], dict(value[2]))
    def _error(self, code):
        return self._response(self._errors[code](code)) if code in self._errors else Response("", code)
    def dispatch(self, path, method="GET"):
        method, path_matches = method.upper(), []
        for pattern, names, methods, func in self._routes:
            match = pattern.fullmatch(path)
            if not match: continue
            path_matches.append(True)
            if method not in methods: continue
            values = match.groupdict()
            for name, kind in names:
                if kind == "int": values[name] = int(values[name])
            return self._response(func(**values))
        return self._error(405 if path_matches else 404)
