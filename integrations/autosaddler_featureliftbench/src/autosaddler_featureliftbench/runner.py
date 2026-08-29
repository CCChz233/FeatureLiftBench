from __future__ import annotations

import argparse
from pathlib import Path

from autosaddler.v2.config.registry import build_runtime, default_registry
from autosaddler.v2.storage.local import LocalRunStore

from .deepseek_provider import deepseek_provider_factory


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AutoSaddler-FLB with integration-owned providers")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--fork-from-run-id")
    parser.add_argument("--fork-through-sequence", type=int)
    arguments = parser.parse_args()
    if (arguments.fork_from_run_id is None) != (arguments.fork_through_sequence is None):
        parser.error("--fork-from-run-id and --fork-through-sequence must be provided together")

    registry = default_registry()
    registry.providers["deepseek_inline"] = deepseek_provider_factory
    runtime = build_runtime(arguments.config, run_id=arguments.run_id, registry=registry)
    if arguments.fork_from_run_id is not None:
        source = LocalRunStore(
            run_dir=runtime.config.storage.run_root / arguments.fork_from_run_id,
            run_id=arguments.fork_from_run_id,
        )
        runtime.store.fork_from(source, through_sequence=arguments.fork_through_sequence)
    result = runtime.engine.run()
    print(f"selected_candidate_id={result.selected_candidate_id}")
    print(f"development_score={result.development_score:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
