"""Plausible shallow selector: compatibility, specifier and newest-release policy.

Deliberately ordinary implementation, independent of reference internals. It
omits set-dependent hash policy and puts version ahead of binary preference.
"""
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name, parse_wheel_filename, parse_sdist_filename
from packaging.tags import Tag
from packaging.version import Version


def choose_distribution(project, files, *, python_version=(3, 12, 0), supported_tags=("py3-none-any",), specifier="", prefer_binary=False, allow_prereleases=False, allow_yanked=False, allowed_hashes=None, formats=("binary", "source"), ignore_requires_python=False):
    candidates, rejected = [], {}
    tags = {Tag(*tag.split("-")) for tag in supported_tags}
    versions = {}
    for record in files:
        filename = record["filename"]
        wheel = filename.endswith(".whl")
        reason = None
        if record.get("yanked_reason") is not None and not allow_yanked:
            reason = "yanked"
        else:
            try:
                if wheel:
                    name, version, build, wheel_tags = parse_wheel_filename(filename)
                    if not tags.intersection(wheel_tags):
                        reason = "platform_mismatch"
                else:
                    name, version = parse_sdist_filename(filename)
                if canonicalize_name(name) != canonicalize_name(project):
                    reason = "different_project"
                elif ("binary" if wheel else "source") not in formats:
                    reason = "format_unsupported"
                requirement = record.get("requires_python")
                if requirement and not ignore_requires_python:
                    try:
                        if Version(".".join(map(str, python_version))) not in SpecifierSet(requirement):
                            reason = "requires_python_mismatch"
                    except ValueError:
                        pass
            except ValueError:
                reason = "format_invalid"
        if reason:
            rejected[filename] = reason
        else:
            candidates.append(filename)
            versions[filename] = version
    allowed = set(SpecifierSet(specifier).filter(map(str, versions.values()), prereleases=allow_prereleases or None))
    applicable = [name for name in candidates if str(versions[name]) in allowed]
    applicable.sort(key=lambda name: (versions[name], name.endswith(".whl")))
    return dict(candidates=candidates, applicable=applicable, best=applicable[-1] if applicable else None, rejected=rejected)
