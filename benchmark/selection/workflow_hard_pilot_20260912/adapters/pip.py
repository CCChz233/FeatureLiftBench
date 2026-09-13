"""Offline records adapter over the lifted pip candidate-selection implementation."""
from urllib.parse import quote
from packaging.specifiers import SpecifierSet
from packaging.tags import Tag
from . import _engine as e


def choose_distribution(project, files, *, python_version=(3, 12, 0), supported_tags=("py3-none-any",), specifier="", prefer_binary=False, allow_prereleases=False, allow_yanked=False, allowed_hashes=None, formats=("binary", "source"), ignore_requires_python=False):
    tags = [Tag(*tag.split("-")) for tag in supported_tags]
    target = e.TargetPython(python_version, tags)
    checker = e.LinkEvaluator(project, e.canonicalize_name(project), frozenset(formats), target, allow_yanked, ignore_requires_python)
    candidates = []
    rejected = {}
    for record in files:
        link = e.Link("https://offline.invalid/" + quote(record["filename"]), requires_python=record.get("requires_python"), yanked_reason=record.get("yanked_reason"), hashes=record.get("hashes"))
        reason, detail = checker.evaluate_link(link)
        if reason == e.LinkType.candidate:
            candidates.append(e.InstallationCandidate(project, detail, link))
        else:
            rejected[record["filename"]] = reason.name
    evaluator = e.CandidateEvaluator(project, tags, SpecifierSet(specifier), prefer_binary, allow_prereleases, e.Hashes(allowed_hashes) if allowed_hashes is not None else None)
    result = evaluator.compute_best_candidate(candidates)
    return {
        "candidates": [c.link.filename for c in result.all_candidates],
        "applicable": [c.link.filename for c in result.applicable_candidates],
        "best": result.best_candidate.link.filename if result.best_candidate is not None else None,
        "rejected": rejected,
    }


__all__ = ["choose_distribution"]
