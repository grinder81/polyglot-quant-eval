# Independent research-package review

Reviewed 25 October 2026 by the overlap-review agent, separately from the main synthesis author. Disposition: **no blocking issue found within the checks below**. This is a documentation review, not a replication, comprehensive citation audit, or approval to run experiments.

## Files actually checked

- `README.md`: research-review entry and relative link.
- `docs/research-landscape.md`: complete synthesis, T1 table, contribution boundaries and follow-up gates.
- `docs/research-search-coverage.md`: complete coverage ledger, public/community distinction, scope and unresolved leads.
- `docs/research-primary-evidence.md` and `docs/research-community-resources.md`: complete text for consistency, evidence-depth labels, numerical caveats and nonclaims.
- `docs/research-overlap-audit.md`: complete text; authored by this reviewer, so this is a consistency check rather than an independent review of that file.
- `results/t1-cold-baselines/README.md`: all synthesis T1 numerical values and interpretation checked against this existing report.
- `docs/stage2-plan.md`, `docs/margin-flip-analysis.md` and `CLAUDE.md`: scope, protected-pool/control rules and existing different-option flip definition.

## Findings and corrections incorporated

The synthesis's T1 correct counts, accuracy-change intervals, English-relative intervals, churn counts/rates, source-bootstrap specification and historical-to-fresh Q4 maximum score differences all match the existing T1 README. The churn ratio and the absence of an equivalence/mechanism conclusion are consistent with that report. This check did not recompute raw-shard statistics or bootstrap draws.

Earlier reviewer feedback identified two wording improvements; the synthesis author incorporated both: explicit citation of the close Bavarian/German/English study, and an exploratory margin/churn association row that no longer reads as a validated prediction. The revised row also preserves the distinction between already inspected development membership and untouched holdout.

Targeted primary-source spot checks confirmed the ledger's flagged prose/table discrepancies in [the MT paper, Section 6 and Tables 7–8](https://arxiv.org/html/2508.20893v1), [the Bangla paper, Tables 2–4 and observations](https://arxiv.org/html/2608.24615v1), and the calibration mismatch in [TASA, Table 2](https://arxiv.org/html/2607.00908v1). Those remain reporting ambiguities rather than corrections to the external papers. The separate overlap audit records direct reading of the correctness-flip definitions, FlipEval README fields and the regional-language evaluation protocol.

Across the package, completed T1 evidence remains separate from planned allocation, generation, device and safety work. Broad novelty and absence-of-prior-art claims are rejected. Correctness-state churn and all-choice churn remain distinguished. Source-reading depth is explicit; mutable repositories and abstract-only leads are not presented as reproduced evidence.

Privacy review found public scientific/resource links and access-controlled channel navigation links, but no copied private messages, member identities, meeting credentials, annotation sheets or contact lists. Channel links are explicitly navigation aids rather than public scientific evidence. This reviewer did not independently inspect or reproduce the Discord searches; their coverage descriptions remain the synthesis author's recorded search history.

A local automated existence check found no broken relative Markdown file links in README and the five research documents then present. `git diff --check` was clean. No other author's file was modified by this reviewer during this final pass; this record is the only new edit.

## Remaining limitations

External code, datasets, model weights and results were not executed or audited. Final PDFs and all appendices were not exhaustively reread; source depth remains as stated per ledger. Public URL availability and exact mutable revisions were not all rechecked. T1 raw archives were not revalidated here. The review does not establish source licenses for reuse, available community participation, independent confirmation of author results, or novelty of the eventual intervention. These are retained follow-ups, not implied scientific findings or new experiment authorization.
