# Research — issue #52 Sirach MT witness-lacuna against Greek material

## Direct observed evidence

The complete 46-file CATSS audit in `docs/research/issue-50-mt-apparent-minus.md`
counted **4,278** zero-Hebrew/nonempty-Greek alignments with the first
Hebrew column-A marker `[..]`, **all** in `27.Sirach.par`.
That marker is *not* `--+` (source-judged Greek addition) or `---`
(apparent minus relative to MT); the CATSS notation table and parser
already type `[..]` as `sirach_lacuna_or_illegible` in the
`sirach_manuscript` family. Existing parser regression uses the actual
source-like Sirach 2:13 row `[..]\tOU)AI\\ {t?}`.
The latest complete-corpus materialization of PR #99 still reports
4,305 unclassified technique rows. Issue #60 tracks a *different*
physically empty MT-cell row at Sirach 19:14; do not generalize to it.

## Data-model discrepancy

`derive_technique_state` currently refuses every Hebrew-empty,
Greek-nonempty state without an explicit Greek plus, MT apparent minus,
or transposition marker. `derive_alignment_technique` does not consult
the already typed Sirach manuscript annotation. As a consequence, the
canonical alignment and annotation nodes survive with raw provenance
but the derived `catss_tt_status` remains `unclassified` on these
known witness-lacuna rows. The LXX projection filters Hebrew-side
annotations out of Greek-word semantic features by default, so a
mapped Greek word cannot expose the relevant missing-Hebrew-witness
context without resorting to sidecars/source parsing. Sirach has no
BHSA parent word/verse model and must **not** be attached to an
unrelated BHSA biblical verse.

## Proposed constrained interpretation

Use an affirmative, documented **Sirach MT-A manuscript lacuna** as
the only additional admissible Hebrew-empty/Greek-nonempty class.
The predicate must be source-specific (`27.Sirach.par`), position-
specific (first token of column A is exactly `[..]`), and supported
by `Annotation(side="mt_a", kind="sirach_lacuna_or_illegible")`.
A bare zero MT count, Greek-side `[..]`, reconstructed `[]`,
marker only in MT-B, or physically empty MT-A do NOT qualify.

For this class retain cardinality `zero_one` / `zero_many`,
`token_balance_mt_lxx=not_applicable`, and both
`addition_vs_mt=False` and `omission_vs_mt=False`.
No Greek/MT translation judgment is implied. Canonical first-class
annotation nodes already encode the source/side/marker/raw. In the
LXX projection, permit only this exact MT-A witness-lacuna annotation
to cross onto matched Greek lexical memberships, preserving
`catss_sem_sirach_lacuna_or_illegible_mt_a` scope. The generic MT-side
annotation-crossing filter stays restrictive for all other kinds.
No BHSA anchor is valid for Sirach.

The typed projection membership schema also independently derives
technique state. It needs the *same* narrow admission rule, validated
with `membership.source`, scoped semantic evidence, and no plus
flag. It must reject forged metadata (the annotation supplied on the
Greek side, a different source, or a falsely claimed plus).
Avoid adding a redundant general zero-MT acceptance path.

## Review hazards

Challenge source/scope spoofing, broadened first-token recognition,
the manuscript-vs-translation distinction, the failure to propagate
source provenance onto Greek memberships, and changed counts in
unrelated books. Evaluate actual source distribution and final
`unclassified_techniques` count from the pinned full 46-file run.
A green test matrix without that data run is insufficient.
