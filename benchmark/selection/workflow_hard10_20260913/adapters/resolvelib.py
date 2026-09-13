from dataclasses import dataclass
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version
from resolvelib import Resolver, BaseReporter
from resolvelib.providers import AbstractProvider
from resolvelib.resolvers import ResolutionImpossible, ResolutionTooDeep


@dataclass(frozen=True)
class _Candidate:
    name: str
    version: Version
    extras: frozenset
    dependencies: tuple


def resolve_dependencies(index, requirements, *, constraints=(), environment=None, prereleases=False):
    env = dict(implementation_name='cpython', implementation_version='3.12.0',
               os_name='posix', platform_machine='x86_64', platform_release='',
               platform_system='Linux', platform_version='', python_full_version='3.12.0',
               platform_python_implementation='CPython', python_version='3.12', sys_platform='linux')
    env.update(environment or {})
    def parse(text):
        req = Requirement(text)
        if req.url:
            raise ValueError('URL requirements are excluded')
        return req
    def active(req, extras=()):
        return req.marker is None or any(req.marker.evaluate({**env, 'extra': e}) for e in ('', *sorted(extras)))
    catalog = {}
    seen = set()
    for row in index:
        name, version = canonicalize_name(row['name']), Version(row['version'])
        if (name, version) in seen:
            raise ValueError('duplicate release')
        seen.add((name, version))
        catalog.setdefault(name, []).append((version, tuple(row.get('dependencies', ()))))
    limits = [parse(s) for s in constraints]
    limits = [r for r in limits if active(r)]

    class Provider(AbstractProvider):
        def identify(self, requirement_or_candidate):
            return canonicalize_name(requirement_or_candidate.name)

        def get_preference(self, identifier, resolutions, candidates, information, backtrack_causes):
            return identifier

        def find_matches(self, identifier, requirements, incompatibilities):
            required = list(requirements[identifier])
            extras = frozenset(e for r in required for e in r.extras)
            restrictions = required + [r for r in limits if self.identify(r) == identifier]
            blocked = set(incompatibilities[identifier])
            return [c for version, deps in sorted(catalog.get(identifier, []), reverse=True)
                    if all(r.specifier.contains(version, prereleases=prereleases) for r in restrictions)
                    if (c := _Candidate(identifier, version, extras, deps)) not in blocked]

        def is_satisfied_by(self, requirement, candidate):
            return (self.identify(requirement) == candidate.name
                    and requirement.extras <= candidate.extras
                    and requirement.specifier.contains(candidate.version, prereleases=prereleases))

        def get_dependencies(self, candidate):
            return [r for s in candidate.dependencies if active(r := parse(s), candidate.extras)]

    provider = Provider()
    roots = [r for s in requirements if active(r := parse(s))]
    try:
        result = Resolver(provider, BaseReporter()).resolve(roots, max_rounds=10000)
    except (ResolutionImpossible, ResolutionTooDeep) as exc:
        raise ValueError('unsatisfiable dependency set') from exc
    return {name: {'version': str(c.version), 'extras': sorted(c.extras),
                   'dependencies': sorted({provider.identify(r) for r in provider.get_dependencies(c)})}
            for name, c in sorted(result.mapping.items())}
