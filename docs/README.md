# Documentation Index

This index separates **current operating docs** from historical/reference material. If two docs disagree, prefer the current operating docs below.

## Current Docs

| Need | Canonical doc |
| --- | --- |
| Project overview | [../README.md](../README.md) |
| What the benchmark measures | [CONCEPTS.md](CONCEPTS.md) |
| Reproducible benchmark contract | [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) |
| Current commands | [../RUN.md](../RUN.md) |
| OpenHands server runs | [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md) |
| Environment and Docker setup | [SETUP.md](SETUP.md) |
| Task directory and metadata format | [TASK_FORMAT.md](TASK_FORMAT.md) |
| Task catalog | [benchmark_tasks.md](benchmark_tasks.md) |
| Architecture and paths | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Known limitations | [limitations.md](limitations.md) |

## Current Experiment Direction

The active evaluation path is:

```text
OpenHands agent
  -> agent Docker
  -> FeatureLiftBench workspace
  -> submission/featurelifted
  -> eval Docker
  -> run.json / suite.json / context audit
```

OpenHands is the main agent because it has built-in context management. The harness records prompt-token evidence through the local OpenAI-compatible proxy when the provider returns usage fields.

`mini-swe-agent` remains useful as a legacy baseline, but append-only history runs are not sufficient for long-context claims unless rerun with verified context handling.

## Reference Docs

These docs are still useful, but they are not the main run path:

| Doc | Status |
| --- | --- |
| [OPENHANDS_BENCHMARK_TODO.md](OPENHANDS_BENCHMARK_TODO.md) | Current OpenHands implementation checklist and remaining hardening items |
| [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md) | Condensed lessons from server failures |
| [SERVER_DEPLOY.md](SERVER_DEPLOY.md) | Server checklist for OpenHands 100-task main suite |
| [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) | Historical mini-swe-agent/vLLM/SiliconFlow results; not current long-context main claim |
| [FLASH_PRO_EXPERIMENT_ANALYSIS.md](FLASH_PRO_EXPERIMENT_ANALYSIS.md) | Historical Flash/Pro analysis under earlier protocols |
| [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) | Older benchmark status notes |
| [FEATURELIFT_AGENT_DESIGN.md](FEATURELIFT_AGENT_DESIGN.md) | Design of in-repo control scaffold |
| [FEATURELIFT_AGENT_TODO.md](FEATURELIFT_AGENT_TODO.md) | Control-scaffold backlog |

## Dataset Curation Docs

| Doc | Use |
| --- | --- |
| [../BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) | Batch-1 task authoring workflow |
| [BATCH1_REPO_SELECTION.md](BATCH1_REPO_SELECTION.md) | Repository selection policy |
| [BATCH1_QUALITY_RUBRIC.md](BATCH1_QUALITY_RUBRIC.md) | Task quality review gates |
| [EXPANSION.md](EXPANSION.md) | Expansion notes |
| [candidate_backlog.md](candidate_backlog.md) | Candidate repository backlog |

## Go Exploration Docs

Go support is exploratory and not part of the current Python OpenHands mainline.

| Doc | Use |
| --- | --- |
| [../GO_FEATURELIFTBENCH_DESIGN.md](../GO_FEATURELIFTBENCH_DESIGN.md) | Go benchmark design |
| [GO_V2_MINI_SPEC.md](GO_V2_MINI_SPEC.md) | Go pilot task/eval contract |
| [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) | Go pilot execution notes |
| [go_task_designs/TEMPLATE.md](go_task_designs/TEMPLATE.md) | Go task design template |

## Task Design Notes

`docs/task_designs/*.md` are human design notes for individual tasks. They are not the machine-readable source of truth. The executable task contract is the task directory plus [TASK_FORMAT.md](TASK_FORMAT.md).
