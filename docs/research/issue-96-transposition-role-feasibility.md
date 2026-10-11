# R96-14 — transposition-role-aware CATSS Greek candidate feasibility

## Evidence in live code and pinned sources (2026-10-11)

Main `dd76f398d4a7d3a8a9c72a6b6eb47ebb8894aa6f`. The production `src/catss_tf/lxx_resolver.py::_placements_conflict` rejects every overlapping candidate *except* an **identical word interval** carried by the exact pair of roles `transposition_alignment` and `transposition_carrier`. The role `_mapping_kind` is determined by typed `AlignmentRecord.annotations`, **not** merely the occurrence of Greek words or raw marker text: Greek-side `transposition_stylistic`/`transposition_remote` -> alignment; MT-A-side `transposition_remote` with exactly `{...}` -> carrier; otherwise exact. `tests/test_lxx_resolver.py::test_stylistic_transposition_proxy_and_carrier_may_share_parent_words` exercises actual parsed `Gen 1:29` example `ZR(\\t{..^SPORI/MOU}` and `{...}\\tSPORI/MOU`, both mapping to the identical Greek word. It is therefore false to treat every duplicate lexical candidate as a strict placement conflict in the exploratory read-only audit.

The existing `src/catss_tf/reference_surface_audit.py::_classify_joint_intervals` uses a strict half-open overlap conflict across all roles. The current 46 CATSS file / pinned CenterBLC/LXX audit ([workflow 38151627799](https://github.com/alexsosn/CATSS-TF/actions/runs/38151627799)) has 6,218 scalar references and **671** explicit reference groups: 326 unique, 70 multiple, 19 conditionally impossible, 256 incomplete, 0 indeterminate. The R96-13 contextual hypothesis puts unreferenced/default Greek lexical rows in the same parent key for **279** scopes and classifies the same 671 as 252 unique, 75 multiple, 49 impossible, 295 incomplete, 0 indeterminate. Their impossibility and uniqueness assume disjoint word intervals even when the production resolver's narrowly grounded role exception applies.

The CATSS source `Gen 1:29` fixture justifies a **separate role-aware conditional model** for the same existing explicit-reference groups; it does not establish the underlying meaning of CATSS scalar references nor prove that the default MT header truly denotes a Greek lexical target. Cross-verse assignment and Greek-empty placeholders remain out of scope. Neither parent word IDs nor corpus bytes may be committed.

## Proposed milestone / constraints

- Preserve **all** existing scalar, `joint_*` and `context_*` counts and classifications unchanged. Add a distinct `role_context_*` five-way outcome partition over exactly those **671** explicit-reference scopes, plus `role_context_changed_groups` and `role_context_groups_with_eligible_pair` evidence counts.
- Reuse production `_mapping_kind` to derive each lexical alignment's role from annotations rather than duplicating classification semantics, including both explicit and implicit/default contenders. Keep source-name and exact parent book/chapter/verse/subverse identity isolation; no cross-group role sharing.
- Extend the existing lazy bounded DFS with optional role-aware collision checks. An overlap is compatible **only** if both ranges have identical start/stop and the two distinct tasks' roles form exactly `{transposition_alignment, transposition_carrier}`. Partial overlap, exact-vs-carrier, two carriers, two alignment roles, or any third competing exact task still conflict. Distinct assignments must remain distinct even if two rows point to the same Greek interval, and the visit budget must still return `indeterminate` on unresolved alternatives.
- Deduplicate repeated scalar references belonging to the same alignment ID as before. If one role-aware group is incomplete due to a missing explicit or implicit lexical candidate, remain `incomplete` rather than computing a hypothetical solution. No verified semantic target edges created.
- Compute role-aware classifications on **all existing reference groups**, even when no implicit default row joins, because two *explicit* CATSS rows could bear the complementary roles. Report the number of groups with at least one complementary pair (source-level roles, not necessarily overlapping candidate intervals) and how many final role-aware outcomes differ from strict context.
- CI must verify the pinned 46-source corpus and report observed counts **only after running**; do not predict numerical effects, and keep #96 open.

## Research and test gates

1. Commit this grounded research and a written plan before RED.
2. Commit failing semantic regressions: identical interval role-pair allowed, unrelated exact role rejected, partial overlap rejected, third contender blocked, ambiguous assignments still multiple, bounded budget indeterminate. Include a real parser notation fixture sharing a Greek word via an explicit alignment and implicit carrier. Verify RED pytest failure for intended reason before production changes.
3. Implement the smallest role-parametric DFS + context role bookkeeping while preserving strict DFS default and all original counters.
4. Run Python 3.11–3.13, Ruff, mypy, release smoke, complete CCAT source and pinned parent audit, and Text-Fabric canonical corpus materialization/readback. Record actual `role_context_*` counts in research and CI.
5. Independently adversarially review exact head using real code and data: attempt to forge overlap through raw spelling, misuse transposition roles, conflate reference scopes, fake multiple solutions through same alignment, trigger memory/cutoff defects, change previous counters or emit speculative target mappings. Fix any blocking findings via RED and rerun exact-head CI and review before merge.


## RED evidence

Regression tests were committed first in `2cfb86b45904d5c9bd91694f1f5c3a982ac81317`. A targeted rerun of that original *preimplementation* SHA ([workflow 38155269932, attempt 2](https://github.com/alexsosn/CATSS-TF/actions/runs/38155269932), Python 3.11 job 114517952269) passed Ruff/format and then **failed at mypy** with precisely 10 intended missing-contract findings: `_classify_joint_intervals` rejects the new `roles` parameter, and `LxxReferenceSurfaceCandidates` lacks the new role-context fields. Since the type gate was RED, the workflow did **not** execute pytest; do not misreport this as behavioral pytest RED evidence. Existing behavioral fixtures and their expected outcomes remain committed, to be verified by the GREEN pytest matrix. Running the original SHA after a newer head had queued canceled that newer run due to the configured pull-request workflow concurrency; the subsequent final-head GREEN must be rerun separately.


## Observed pinned 46-file CATSS / CenterBLC-LXX outcome (2026-10-11)

[GREEN workflow 38156016173](https://github.com/alexsosn/CATSS-TF/actions/runs/38156016173) on code head `551d930f6289fb0f5f4c5deb60043f42b32d22e7`: **505 pytest tests each** on Python 3.11/3.12/3.13, Ruff, formatter, mypy, clean wheel/release smoke, entire 46-source CATSS source/notation and pinned LXX checks, full canonical Text-Fabric materialization and readback. The source-audit job `114519040026` printed the unchanged 6,218 scalar references; 4,349 local exact singles (232 overlaps = 108 unavoidable + 124 optional-only); 4,117 singles without overlap; 455 multiple, 294 no surface, 453 Greek-empty, 641 parent missing, four CATSS normalization errors, 22 unsupported. Original 671 explicit-only groups **326/70/19/256/0**, and 671 strict default-context groups **252/75/49/295/0** are unchanged.

The *new* conditional model found **96 groups** containing both transposition-alignment and transposition-carrier roles. The strict default-context classification changed in **17 groups** when identical interval sharing was permitted for exactly this role pair.

| Outcome (same 671 explicit-key scopes) | Strict default-context | Role-aware context |
| --- | ---: | ---: |
| Unique | 252 | **260** |
| Multiple | 75 | **84** |
| Impossible | 49 | **32** |
| Incomplete | 295 | **295** |
| Indeterminate | 0 | **0** |

The strict impossibility count falls by 17; uniqueness rises by eight and multiplicity by nine. Given the role-aware rule *only relaxes* a conflict (without changing candidate sets), no case can move from possible to impossible. On this pinned dataset (no indeterminate outcomes), the 17 changed classifications therefore consist of eight conditional impossible→unique and nine conditional impossible→multiple. **These are not resolved CATSS errors or verified targets**. Their default Greek parent key derives from a CATSS MT header unless a real scalar reference overrides it; typed transposition roles may share an LXX surface yet the reference notation itself remains unverified. The remaining 32 impossible groups may reflect contextual notation, a missing cross-key model, or other provenance issues.

No LXX word IDs, source lines, or raw corpora are emitted. Before finalizing the PR, repeat the identical pinned counts as CI assertions on the last reviewed exact head (this run preceded the new documentation/pins). Leave issue #96 OPEN.
