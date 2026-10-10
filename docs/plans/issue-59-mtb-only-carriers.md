# Plan — issue #59, typed canonical MT-B-only carriers

Research: [issue-59-mtb-only-carriers.md](../research/issue-59-mtb-only-carriers.md).

## RED-first tests

- Synthetic `12.2Sam.par` with two *identical* `=;W/KL` rows, a
  synthetic `17.1Esdras.par` with `=W/M/BNY` and a
  `44.Ezekiel.par` with `=v`. Require four **distinct**
  `mt_b_carrier` TF nodes (including both duplicate-text source rows),
  one per alignment slot, raw column-B payloads `;W/KL`,
  `W/M/BNY`, `v`, and typed kinds `context`, `plain`,
  `vocalization`. Require zero `mt_element` nodes for those
  alignments; no `catss_tt_addition_vs_mt` fabricated.
- Mixed synthetic verse with a normal MT-A lexical `HB=;WORDS`
  must preserve a true `mt_element` and **not** create a separate
  `mt_b_carrier` (this milestone is explicitly empty-A scoped).
- Assert preservation audit counts and deterministic byte-identical
  re-materialization in two directories.

Commit the RED before modifying the writer, and record an actual
intentional test failure. Keep checks from RED from accidentally merging.

## GREEN implementation

Add a contiguous type block for `mt_b_carrier` to
`_add_detail_nodes`; validate one carrier for every `mt_count==0`,
`lxx_count>0` and `mt_col_b is not None` in `_audit_graph`.
The prior overbroad condition produced 8,887 false-positive carriers on
the actual 46-file source; a Greek-empty RED counterexample must fail
before this scope correction. The node has one
alignment slot, raw B string and retro kind, no purported Hebrew lexical
token. Update researcher docs, not generic parser or parent projections.
Do not alter the 349,670 source alignment count, 350,219 genuine MT
elements, Greek counts, source-line provenance or strict technique API.

## Real-data / release gates

- Complete 46-file audit: **exactly six** `mt_b_carrier` nodes in the
  scoped source snapshot; distribute across 2Sam (4), 1Esdras (1),
  Ezekiel (1) and assert the `=v` carrier is typed `vocalization`.
- TF `Fabric.load` readback queries the new feature and group identity.
- Python 3.11/3.12/3.13, format, lint, mypy, release smoke, full 46-file
  audit, stable TDD failure evidence; no corpus distributions.
- Logically independent adversarial exact-head review, especially
  duplicate rows, distinction from MT-A, no false lexical reconstruction,
  and no fabricated correspondence to BHSA or LXX.
