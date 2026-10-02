# Plan — issue #87 Exod 35:19 source-layout corruption

Research basis: [issue-87-exod-35-19-layout-repair.md](../research/issue-87-exod-35-19-layout-repair.md).

## Gate 1 — RED focused parser test

Commit a test-only fixture containing the exact seven-line corruption window plus enough
context to establish Exod 35:19.

Require:

1. one Exod 35:19 logical continuation using original lines corresponding to the first
   continued row and orphan `\t#`;
2. `--+\tE)N AU)TAI=S` remains the following independent alignment;
3. no synthetic/corrupt Exod 1:10 verse record;
4. zero `malformed_continuation` diagnostics;
5. one explicit layout-repair provenance record preserving every raw physical line,
   including blanks and duplicate/corrupt headers;
6. surviving source line numbers are the original physical numbers;
7. alignment IDs remain deterministic from those original physical rows.

Observe RED before production changes.

## Gate 2 — exact layout normalizer

Introduce a small pre-header source-line normalization stage. It operates on
`(line_no, raw)` records and returns semantic records plus explicit repair provenance.

Match only the full known `02.Exodus.par` corruption signature. On any mismatch,
return the original stream unchanged.

Do not reuse the existing cell-level source-repair table: this defect changes line/header
structure before cells exist.

## Gate 3 — negative tests

Prove that:

- the same raw fragment in another source filename is not repaired;
- changing `Exod 1:10` to another header prevents the repair;
- changing either continuation row prevents the repair;
- normal header transitions while a continuation is pending are not globally ignored.

## Gate 4 — projection/provenance compatibility

Ensure the new `ParallelDocument` provenance field has a backwards-compatible empty
default or update all constructors/callers explicitly.

Projection materializers must continue to consume repaired alignments with stable source
line identities. Do not serialize multi-line provenance into an opaque feature blob.

Record the canonical-corpus integration requirement for PR #47 so standalone CATSS can
preserve the repair provenance natively.

## Gate 5 — complete-snapshot guard

On the exact downloaded CATSS snapshot:

- locate the known signature exactly once;
- parse `02.Exodus.par`;
- assert one matching layout repair;
- assert the repair's original/surviving lines and raw bytes;
- assert the affected Exod 35:19 sequence is reconstructed;
- assert no malformed-continuation finding remains for the repair window;
- assert no corrupt Exod 1:10 verse is emitted there.

## Gate 6 — exact-head GREEN and adversarial review

Require ruff/format, mypy, Python 3.11/3.12/3.13, release smoke and complete CATSS audit
on the exact final SHA.

Then independently re-review the implementation against both the raw upstream snapshot
and `codykingham/CATSS_parsers`' documented patch. Any broadened repair matcher,
renumbered provenance, or hidden raw line is a blocker.
