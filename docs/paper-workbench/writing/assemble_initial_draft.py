"""One-time assembly of the 2026-09-07 draft; requires explicit --assemble.

The editable paper is ../main.tex. Do not rerun after manually editing it.
Use update_tables.py to refresh only data tables in that file.
"""
from pathlib import Path
import re
import shutil
import sys

PAPER = Path(__file__).resolve().parents[1]
WORK = PAPER / 'writing'


def placeholder(label, title, design, caption, description, height='3.4cm'):
    return '\n'.join([
        r'\begin{figure}[tbp]', r' \centering',
        rf' \figureplaceholder{{{height}}}{{{title}}}{{{design}}}',
        rf' \caption{{{caption}}}', rf' \Description{{{description}}}',
        rf' \label{{{label}}}', r'\end{figure}', '',
    ])


def marker(key):
    return f'% BEGIN GENERATED TABLE: {key}\n% END GENERATED TABLE: {key}\n'


def main():
    if sys.argv[1:] != ['--assemble']:
        raise SystemExit('Historical assembler: pass --assemble explicitly; this overwrites main.tex.')
    for name in ['main.tex', 'references.bib', 'main.pdf']:
        src = PAPER / name
        dst = WORK / ('original_' + src.stem + '_20260907' + src.suffix)
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    s = (WORK / 'manuscript.tex').read_text(encoding='utf-8')
    s = s.replace(r'\graphicspath{{figures/}}', r'''% Replace each \figureplaceholder call with \includegraphics when artwork is ready.
\newcommand{\figureplaceholder}[3]{%
  \begingroup\setlength{\fboxsep}{9pt}%
  \fcolorbox{black!35}{black!3}{%
    \begin{minipage}[c][#1][c]{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}
      \centering\small\textbf{#2}\par\medskip
      \textit{Figure placeholder --- artwork to be added}\par\medskip
      #3
    \end{minipage}}\endgroup}
\graphicspath{{figures/}}
\setlength{\emergencystretch}{2em}''')
    s = s.replace('Evaluating Behavior-Preserving Feature Extraction', 'Benchmarking Behavior-Preserving Feature Lifting')
    s = s.replace('Our main study\ncompares six model backends in OpenHands on a common 150-task subset, with source\nlocation hints and benchmark tests withheld.', 'Our main study\nreports existing OpenHands campaigns for six model backends on 150 common task\nIDs, with source-location hints and benchmark tests withheld. We disclose\nbackend-specific context handling and retained results with two freeze identities.')
    s = s.replace('% RELATED_WORK_INSERT\n', '')
    s = s.replace(r'\subsection{Task and Output Boundary}', r'\subsection{Task Formulation and a Running Example}')
    start = s.index(r'\begin{figure}')
    end = s.index(r'\end{figure}', start) + len(r'\end{figure}')
    example = r'''\paragraph{Running example: a signal registry.}
The Blinker task asks for \texttt{Signal}, \texttt{Namespace}, and \texttt{ANY}
under the new \texttt{featurelifted} namespace. The public contract requires
sender-specific dispatch, receiver responses, cleanup of weak receivers after
garbage collection, stable signal identity within a namespace, and scoped
connection/disconnection. It excludes asynchronous receivers and the upstream
global named-signal singleton. A plausible dispatcher can therefore remain
incomplete even if its main \texttt{connect} and \texttt{send} methods work:
receiver lifetime and namespace identity are also part of the requested behavior.
The final artifact may retain upstream code or reimplement these obligations,
but may not import \texttt{blinker} or read the donor tree at runtime.
Figure~\ref{fig:pipeline} summarizes this source-to-artifact boundary using only
the public task contract.

'''
    s = s[:start] + example + placeholder('fig:pipeline', 'Task example and source-to-artifact boundary',
        r'Intact Blinker repository + public contract $\rightarrow$ agent $\rightarrow$ new package.\\Show dispatch, weak-receiver lifetime, and namespace identity as obligations.\\Only the artifact enters source-free evaluation.',
        r'Feature lifting on the signal-registry task. The complete donor repository supplies implementation evidence; the new package must preserve the declared behavior without runtime access to that repository. Both benchmark test groups and reference solutions are withheld from the agent in Main.',
        'Planned task schematic showing the public signal-registry obligations, available source evidence, submitted package, and source-free evaluator.') + s[end:]
    s = s.replace(r'\subsection{Task Construction and Freezing}', r'\subsection{Task Construction and Source Provenance}')
    s = s.replace('The freeze v2 repair process', r'\subsection{Validation Evidence and Quality Boundaries}'+'\n\\label{sec:validation}\n\nThe freeze v2 repair process', 1)
    s = s.replace(r'Table~\ref{tab:validation}', r'Table~\ref{tab:dataset}')
    for label in ['validation', 'construction', 'main', 'funnel', 'independent-gates', 'compactness', 'extension', 'semantic']:
        pattern = r'\\begin\{table\}\[[^\]]*\](?:(?!\\end\{table\}).)*?\\label\{tab:' + re.escape(label) + r'\}(?:(?!\\end\{table\}).)*?\\end\{table\}'
        key = {'main': 'main', 'extension': 'extension', 'semantic': 'semantic'}.get(label)
        s, n = re.subn(pattern, lambda m: marker(key) if key else '', s, flags=re.S)
        assert n == 1, (label, n)
    validation_fig = placeholder('fig:construction', 'Benchmark construction and validation evidence',
        r'Pinned source $\rightarrow$ bounded public contract $\rightarrow$ protected tests/reference $\rightarrow$ mechanical checks and oracle replay $\rightarrow$ release.\\Mark agent-visible and evaluator-only assets; attach only documented counts.',
        r'Construction and evidence boundaries. The release records 200 task checks, 200 source mappings, and 600 passing reference executions. Repair-scope review covers 38 tasks. These checks establish recorded feasibility and consistency; they do not constitute a complete independent semantic audit.',
        'Planned construction diagram separating public assets, protected evaluation assets, and the documented validation checks.')
    s = s.replace(r'\subsection{Suite Composition}', validation_fig + '\n' + r'\subsection{Dataset Composition}')
    s = s.replace(r'Table~\ref{tab:construction}', r'Table~\ref{tab:dataset}')
    s = s.replace('The 200-task release consists of Python-150', 'Figure~\\ref{fig:construction} distinguishes construction from completed validation.\nThe 200-task release consists of Python-150')
    s = s.replace('cannot support an empirical difficulty contrast here.', 'cannot support an empirical difficulty contrast here. Canonical repository IDs\nin the freeze identify 126 repositories in Python-150 and 50 in the extension,\nwith no overlap, for 176 in the complete release. Repository aliases are\nnormalized before counting.\n\n' + marker('dataset'))
    s = s.replace(r'\section{Evaluation Protocol and Study Design}', r'\section{Evaluation Protocol and Experimental Setup}')
    s = s.replace(r'\subsection{Agent Conditions and Recorded Runs}', r'\subsection{Information Boundary and Agent Configurations}')
    begin = s.index('The analysis retains one collected outcome')
    end = s.index(r'\subsection{Source-Free Functional Evaluation}', begin)
    assembly = r'''The analysis retains one collected outcome per model--task cell, yielding
900 cells over 150 common task IDs. Empty submissions remain failures, including
tool-validation and early-exit events. Run status is separate from evaluator
correctness. The campaign includes preflight replacements and runner-level
transient recovery, whose records are retained. We report the final collected
functional outcome under that policy; this is not a repeated-run estimate or a
claim that every task used exactly one uninterrupted process invocation.

\paragraph{Merged campaign provenance.}
The release specification has freeze identity \texttt{6c20ff03\ldots}, but the
result matrix retains 522 rows with that identity and 378 with predecessor
identity \texttt{0b106842\ldots}. Pro, GLM, and OSS each contribute 150 v2 rows;
Flash, Luna, and Qwen each contribute 24 v2 rows and 126 predecessor rows
(Table~\ref{tab:config}). All rows report the evaluator image tag ending in
\texttt{212930ea}. Agreement of image tags does not establish equivalence of
task contracts or agent-visible inputs. The offline checks used here verify
result counts and recorded gate outcomes, not per-task equivalence across these
freeze identities. Accordingly, the main table is a descriptive comparison of
the retained campaigns on common task IDs, and the statistical comparisons
below are conditional on that assembled record. They do not isolate the effect
of changing only the model backend. Appendix~\ref{app:reproduction} identifies
the relevant evidence files.

'''
    s = s[:begin] + r'''Context handling is not identical across backends. Pro and Flash use the
token condenser with a 122,880-token trigger and a 61,440-token target; Luna,
GLM, Qwen, and OSS record the default condenser without explicit token thresholds.
Table~\ref{tab:config} reports these settings and the result provenance.

''' + marker('config') + '\n' + s[end:]
    s = s.replace(r'\subsection{Source-Free Functional Evaluation}', r'\subsection{Functional Evaluation and Extraction Metrics}')
    s = s.replace(r'\subsection{Extraction Measurements}', r'\paragraph{Extraction measurements.}')
    s = s.replace(r'\subsection{Statistical and Evidence Boundaries}', r'\subsection{Result Assembly and Statistical Protocol}'+'\n\n'+assembly)
    s = s.replace(r'\section{Results}', r'\section{Benchmark Results}')
    s = s.replace(r'\subsection{RQ1: Functional Capability}', r'\subsection{RQ1: Overall Functional Capability}')
    s = s.replace(r'\subsection{RQ2: Evaluator Failure Outcomes}', r'\subsection{RQ2: Where Do Submissions Fail?}')
    s = s.replace(r'\subsection{RQ3: Observed Task Difficulty}', r'\subsection{RQ3: How Does Task Difficulty Vary?}')
    s = s.replace(r'\subsection{RQ4: Extraction Footprint on Common Successes}', r'\subsection{RQ4: How Compact Are Common Successes?}')
    s = s.replace('The exclusive outcomes in Table~\\ref{tab:funnel}', 'Figure~\\ref{fig:failures} summarizes the failure outcomes.\nThe exclusive counts in Appendix Table~\\ref{tab:funnel}')
    s = s.replace('(Table~\\ref{tab:independent-gates})', '(Appendix Table~\\ref{tab:independent-gates})')
    insert = placeholder('fig:failures', 'Evaluator failures: exclusive outcomes and overlapping flags',
        r'(a) Stacked first-outcome bars, 150 tasks per backend.\\(b) Failed gate flags among delivered artifacts, with denominators shown.\\Distinguish 39 Isolation flags from the four Isolation residuals.',
        r'Where submitted artifacts fail. First outcomes are mutually exclusive; failed gate flags can overlap and use the 829 delivered artifacts as their pooled denominator. Only four artifacts pass Build, Public, and Hidden but fail Isolation. Exact values appear in Tables~\ref{tab:funnel} and~\ref{tab:independent-gates}.',
        'Planned two-panel failure chart distinguishing missing submissions, first failures, non-exclusive failed gate flags, and the Isolation residual.')
    s = s.replace(r'\subsection{RQ3:', insert+'\n'+r'\subsection{RQ3:', 1)
    for label, title, design, caption, desc in [
        ('fig:difficulty', 'Task difficulty across the six recorded configurations',
         r'(a) Counts of tasks passed by 0--6 backends, split into Core and hard3.\\(b) Core/hard3 pass rates for each backend.\\Use the full 150-task view; annotate the separate seven-task exclusion.',
         r'Solve-frequency spectrum and construction-group performance on Python-150. The zero-pass group contains six Core and 22 hard3 tasks; the six-pass group contains 15 Core and two hard3 tasks. These are observed campaign outcomes, not independently calibrated difficulty labels. Tables~\ref{tab:difficulty} and~\ref{tab:main} supply the values.',
         'Planned solve-frequency chart and Core versus hard3 pass-rate comparison.'),
        ('fig:paired-copy', 'Paired extraction footprint on common successes',
         r'Two matched-task panels: reference-relative size and detected copy fraction.\\Primary pair: Pro/Luna, 97 common passing tasks.\\Show paired values and median summaries; keep the two metrics separate.',
         r'Pro and Luna on their 97 common passing tasks. Median RRES is 0.993 versus 0.697; median detected copy fraction is 0.966 versus 0.191. Pairing controls task membership within the retained campaigns. Copying and size describe different artifact properties. Table~\ref{tab:paired} gives the paired summaries.',
         'Planned paired RRES and detected-copy comparison on the same 97 passing tasks.')]:
        pattern = r'\\begin\{figure\}\[t\](?:(?!\\end\{figure\}).)*?\\label\{'+re.escape(label)+r'\}(?:(?!\\end\{figure\}).)*?\\end\{figure\}'
        s, n = re.subn(pattern, lambda m: placeholder(label,title,design,caption,desc), s, flags=re.S)
        assert n == 1, label
    s = s.replace('Table~\\ref{tab:compactness} describes', 'Appendix Table~\\ref{tab:compactness} describes')
    s = s.replace('The paired Wilcoxon test yields', 'The paired Wilcoxon test on copy fractions yields')
    s = s.replace(r'\section{Exploratory Diagnostics and Sensitivity}', r'\section{Diagnostic Analysis and Discussion}')
    s = s.replace(r'\subsection{Contract Defects and Denominators}', r'\subsection{Contract Defects and Sensitivity}')
    s = s.replace('This conservative\ntask-level exclusion', 'This post hoc\ntask-level exclusion')
    s = s.replace('% SENSITIVITY_INSERT', marker('sensitivity')+r'''
All six configurations fail all seven flagged tasks in the existing record.
Exclusion therefore leaves every numerator unchanged while reducing the
denominator to 143: Pro becomes 115/143 (80.4\%), Flash 108/143 (75.5\%), and
Luna 102/143 (71.3\%). The count of tasks passed by none of the six drops from
28 to 21, of which 16 are hard3. The observed pass-count ordering is unchanged,
but the absolute rates and the size of the all-fail group are affected. Because
the flags were found through failure inspection and are provisional, these
values quantify the influence of the identified tasks; they neither certify
the remaining tasks nor replace the 150-task campaign results.
''')
    s = s.replace(r'\subsection{Behavioral-Contract Recovery}', r'\subsection{Exploratory Evidence on Behavioral-Contract Recovery}')
    start = s.index(r'\subsection{Delivery and Interaction Diagnostics}')
    end = s.index(r'\section{Discussion}', start)
    process = s[start:end].replace(r'\subsection{Delivery and Interaction Diagnostics}', r'\subsection{Delivery and Interaction Records}')
    s = s[:start] + s[end:]
    s = s.replace(r'\section{Discussion}', r'\subsection{Implications for Feature-Lifting Agents}')
    s = s.replace('the current results remain attached to their original freeze.', 'the current results retain their recorded run identities.')
    s = s.replace('The release records identities for these components, and the paper does not pool\nearlier freezes or information ablations into the main comparison. Nevertheless,', 'The release records identities for these components. The retained campaigns\ncontain two run-freeze identities, and per-task input equivalence is not\nestablished here. Pro/Flash also use different condenser settings from the\nother backends. These factors limit attribution of score differences to model\ncapability alone. Information ablations are excluded. In addition,')
    related = (WORK/'related_work.tex').read_text(encoding='utf-8')
    related = related[related.index(r'\section{Related Work}'):]
    related = related.replace('issues~\\cite{jimenez2024swebench}.', r'''issues~\cite{jimenez2024swebench}. SWE-Bench Pro emphasizes longer-horizon
engineering tasks and analyzes observed agent failures~\cite{deng2025swebenchpro}.''')
    related = related.replace('Harness-Bench studies variation', r'''OSWorld couples task-specific initial states with execution-based evaluation
for desktop workflows~\cite{xie2024osworld}. These environments show why task
definition, environment reproducibility, and evaluator validity merit separate
description. Harness-Bench studies variation''')
    related = related.replace('We use a fixed OpenHands protocol for the main comparison and', 'We hold the Main information boundary fixed, disclose recorded OpenHands\nprofiles and mixed run provenance, and')
    s = s.replace(r'\section{Conclusion}', related+'\n'+r'\section{Conclusion}')
    s = s.replace('Under the recorded OpenHands Main protocol, functional pass', 'Across the retained OpenHands Main campaigns, functional pass')
    s = s.replace('Exploratory failure evidence and disclosed task-defect sensitivity qualify the', 'Mixed run provenance, exploratory failure evidence, and task-defect sensitivity qualify the')
    s = s.replace('five available 200-task campaigns under\nfreeze v2', 'five available assembled 200-task campaigns')
    s = s.replace('not for a six-backend difficulty or compactness comparison.', 'not for a six-backend difficulty or compactness comparison. The same\nrun-provenance limitation applies: a release task identity is not a claim that\nevery retained execution was newly performed under that freeze.')
    appendix_a = r'''
\section{Task Provenance and Validation Scope}
\label{app:provenance}
The freeze binds each task to its public specification hash, generated task hash,
source repository ID, resolved commit, source-tree and archive digests, task-tree
digest, and reference-tree digest. Canonical IDs are the counting unit for
repository totals. The 150 main tasks and the 50 additional tasks come from
disjoint sets of 126 and 50 repositories. Oracle replay records three successful
executions for each task with stable fingerprints. The 38-task repair scope is
documented separately from the full release checks.

The intended fairness relation is that evaluator expectations refine the public
contract and have support in the pinned source behavior. Schema checks and
reference execution provide only partial evidence for this relation. The current
record does not support a claim that a Validator-Agent or independent human
reviewer has semantically audited every task. The seven later defect flags
illustrate why passing mechanical checks cannot substitute for that audit.

'''
    s = s.replace(r'\appendix', r'\appendix'+'\n'+appendix_a)
    app_tables = r'''
\section{Additional Quantitative Results}
\label{app:quantitative}
The tables below preserve the exact values behind the planned result figures.
First-outcome rows sum to 150. Non-exclusive gate counts use delivered artifacts
and may overlap. Footprint summaries use passing artifacts only. Statistical
tests describe the assembled campaigns and inherit their provenance limitations.

'''+ '\n'.join(marker(k) for k in ['funnel','gates','difficulty','compactness','paired','logistic']) + r'''
The logistic specification is
\begin{equation}
\operatorname{logit}\Pr(F_{mt}=1)
=\alpha+\gamma_m+\beta_h\,\mathbb{1}[t\in\mathrm{hard3}]
+\beta_a\,\mathbb{1}[t\in\mathrm{Adapted}]
+\beta_c\,\mathbb{1}[t\in\mathrm{Composite}].
\end{equation}
Flash, Core, and Direct are the reference categories. Standard errors are
clustered by task. The all-six fit has 900 observations; the Pro/Flash/Luna fit
has 450. Table~\ref{tab:logistic} reports construction/lift coefficients from
the existing fits. Backend coefficients and additional fit output are retained
in the analysis CSV. These regressions cannot remove unmeasured protocol or
provenance differences by conditioning on backend labels.

'''
    s = s.replace(r'\section{Flagged Task Identities and Sensitivity}', app_tables + r'\section{Flagged Task Identities and Sensitivity}')
    s = s.replace('The machine-readable manifest retains', 'The predecessor ID retained by part of the campaign is\n\\begin{quote}\\small\\ttfamily\n0b106842710368a497b49b7f6714e0dfea\\\\\n54778d1fb2dae38c93ea449b339542\n\\end{quote}\nThe machine-readable manifest retains')
    s = s.replace('The paper revision adds only a reproducible offline known-defect sensitivity\ncalculation;', 'The paper revision adds offline table assembly and known-defect sensitivity\ncalculations;')
    s = s.replace('Earlier freezes, development\npilots, alternative information arms, and unrun method proposals are outside the\nmain evidence set.', 'Development pilots, alternative information arms, and unrun method proposals\nare outside the main evidence set. The retained predecessor executions are\nexplicitly counted in Table~\\ref{tab:config}; they are not relabeled as v2 runs.')
    s = s.replace(r'\end{document}', '\n'+process+r'''
\subsection{Offline Reproduction of Paper Tables}
The paper's table updater reads the saved result matrix, freeze manifest,
statistical summaries, annotations, and run metadata. It checks task/model key
uniqueness, denominator consistency, paired-set membership, and numeric
agreement before writing the marked table blocks in the LaTeX source. The
known-defect script additionally checks the 838 existing raw evaluator files;
the other 62 cells have no evaluator result and are retained as failures.
This is offline analysis of saved artifacts, not a new evaluation campaign.
The companion README records input paths and commands. All five main-text
figures are intentionally reserved for author-supplied artwork in this draft;
their captions and appendix data specify the intended content.

\end{document}
''')
    s = re.sub(r'\n{4,}', '\n\n\n', s)
    assert len(re.findall(r'\\section\{', s.split(r'\appendix')[0])) == 8
    assert s.count(r'\begin{figure}') == 5
    assert 'INSERT' not in s and r'\includegraphics[width=' not in s
    (PAPER/'main.tex').write_text(s, encoding='utf-8')
    print('Assembled main.tex: 8 sections, 5 figure placeholders; tables awaiting update.')


if __name__ == '__main__':
    main()
