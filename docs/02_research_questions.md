# Research Questions

## RQ Overview

FeatureLiftBench should use one shared RQ set across all language splits. Python and Go results may be reported in separate tables, but the questions remain the same because both splits test the same capability: standalone, compact, behavior-preserving feature extraction.

| RQ | Question | Primary role |
|---|---|---|
| RQ1 | Can current code agents perform FeatureLift? | Main performance |
| RQ2 | Where do agents fail? | Failure analysis |
| RQ3 | Is feature localization the main bottleneck? | Ablation |
| RQ4 | Is compactness constraint necessary? | Scoring validation |
| RQ5 | What task properties make FeatureLift difficult? | Dataset analysis |

## RQ1: Can Current Code Agents Perform FeatureLift?

Purpose: main performance experiment. This tests whether current code agents can extract standalone reusable features from entangled real-world repositories.

Metrics:

- Pass@1
- Install or build pass
- Public pass
- Hidden pass
- Functional gate
- Final score
- Submitted LOC
- Extraction ratio or LOC ratio
- Forbidden import rate

Expected analysis: report by language split and by agent/model, but do not redefine the task per language.

## RQ2: Where Do Agents Fail?

Purpose: failure analysis. This explains whether failures come from locating the feature, recovering the dependency closure, preserving behavior, packaging the output, or avoiding leakage from the original repository.

Failure types:

- Locate failure
- Dependency closure failure
- Packaging failure
- Behavior drift
- Over-copy
- Forbidden import
- Path leakage
- Test gaming
- Environment failure

Python-specific failure details may involve dynamic imports, monkeypatching, module-level registries, runtime config, and hidden behavior. Go-specific failure details may involve type closure, package boundaries, `go.mod`, interfaces, and compile-time errors. These are subcases under the shared taxonomy, not separate RQs.

## RQ3: Is Feature Localization the Main Bottleneck?

Purpose: distinguish "agent cannot find the feature" from "agent can find it but cannot extract it cleanly."

Core comparison:

| Setting | Agent-visible information | Interpretation |
|---|---|---|
| Standard | Task prompt plus full source repo | End-to-end FeatureLift |
| Hint | Small list of likely relevant files | Reduced localization burden |
| Oracle-Locate | Reference-related files or closure hints | Tests extraction and modularization after localization |

If oracle-locate helps only partially, the benchmark is not merely code search. The remaining gap indicates dependency closure, behavior preservation, and packaging difficulty.

## RQ4: Is Compactness Constraint Necessary?

Purpose: show that tests alone are insufficient. A copy-heavy solution may pass hidden tests while failing the benchmark's reuse goal.

Core experiment:

- Copy-all baseline
- Functional pass rate versus final score
- LOC ratio or extraction ratio distribution
- High-extraction pass versus compact pass

Claim to support: FeatureLiftBench needs both functional correctness and compactness. Without compactness, wholesale copying can look artificially strong.

## RQ5: What Task Properties Make FeatureLift Difficult?

Purpose: explain difficulty drivers and validate task design.

Candidate variables:

- Reference or oracle LOC
- Number of source files in closure
- Dependency depth
- Feature type
- Dynamic behavior
- Global state or registry coupling
- Packaging complexity
- Public-hidden gap
- Language-specific mechanisms such as Python runtime behavior or Go type/package closure

The analysis should avoid claiming causality from small sample sizes. Use correlations and case studies as diagnostic evidence.

## Three Key Experimental Handles

- Copy-all baseline: proves compactness is necessary.
- Oracle-locate baseline: separates localization from extraction and modularization.
- Public-hidden gap: measures behavior drift and public-test overfitting.

## TODO

- Freeze exact model list and agent versions for the paper.
- Define manual failure annotation protocol and inter-annotator policy if used.
- Decide whether `path_leakage` becomes a first-class evaluator metric or remains a failure taxonomy label backed by existing import/path guards.
