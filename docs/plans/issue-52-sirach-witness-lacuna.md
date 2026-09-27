# Plan — issue #52 Sirach Hebrew-witness lacunae

Research basis: [issue-52-sirach-witness-lacuna.md](../research/issue-52-sirach-witness-lacuna.md).

## Gate 1 — RED tests

Before production changes, commit tests proving:

1. parser regression: Sirach MT-side `[..]` remains non-lexical, emits exactly
   one `sirach_lacuna_or_illegible` annotation with `mt_a` scope and
   `sirach_manuscript` family, and preserves raw provenance/alignment identity;
2. direction/scope: the admissibility evidence is exact MT-A
   `sirach_lacuna_or_illegible`, not arbitrary square brackets or same-kind
   annotation on another side;
3. technique: explicit Sirach witness-lacuna evidence admits zero-MT/nonempty-Greek
   cardinality with `addition_vs_mt=False` and `omission_vs_mt=False`;
4. technique: witness-lacuna evidence with nonempty MT or empty Greek fails closed;
5. unexplained zero-MT/nonempty-Greek still fails;
6. LXX materializer: mapped Sirach Greek words expose
   `catss_sem_sirach_lacuna_or_illegible` and the `_mt_a` scoped feature;
7. no `catss_lxx_plus` flag or addition-vs-MT feature is emitted for those
   memberships;
8. BHSA source classification remains unsupported for `27.Sirach.par`.

The RED commit contains no production fix.

## Gate 2 — implementation

Implement the smallest shared semantic change:

- add a technique evidence keyword for MT witness lacuna, default false for API
  compatibility;
- derive that evidence from the exact typed MT-A annotation in
  `derive_alignment_technique()`;
- validate its cardinality fail-closed;
- allow only `sirach_lacuna_or_illegible` with source scope `mt_a` to cross
  onto LXX word memberships;
- pass that semantic evidence into TF membership technique derivation.

Do not:

- change `is_lxx_plus`;
- infer witness lacuna from `mt_n == 0`, source filename alone, or generic
  square-bracket syntax;
- create a BHSA anchor;
- absorb #53 residuals.

## Gate 3 — complete-snapshot guard

Add a complete-current-snapshot invariant requiring exactly **4,278** alignments
with MT-A `sirach_lacuna_or_illegible` evidence and zero MT/nonzero Greek lexical
material.

For every such alignment:

- technique derivation succeeds;
- `addition_vs_mt=False`;
- `omission_vs_mt=False`.

Also assert all guarded rows originate from `27.Sirach.par`.

## Gate 4 — GREEN

Run the exact final head through:

- ruff check and format check;
- mypy;
- pytest on Python 3.11, 3.12 and 3.13;
- release smoke;
- complete-CATSS audit.

## Gate 5 — independent adversarial review

Review the exact green head from scratch and challenge:

- accidental treatment of manuscript lacuna as translation addition;
- filename-only or generic empty-side inference;
- scope leakage from MT-A to unrelated annotations;
- accidental support/anchors on BHSA;
- loss of raw provenance or alignment identity;
- wrong feature placement on LXX structural rather than word nodes;
- interaction with explicit LXX-plus, apparent-minus and transposition rows;
- complete-snapshot count drift.

Any blocking finding returns to RED → fix → GREEN → re-review.

## Downstream acceptance

After #52 merges, merge current `main` into PR #47 and rerun complete canonical
materialization. The Sirach `[..]` population must no longer stop technique
derivation. Any following residual is handled by #53 rather than a broader fallback.
