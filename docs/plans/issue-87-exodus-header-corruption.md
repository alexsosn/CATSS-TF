# Plan — #87 exact Exod 35:19 source-layout repair

1. **Research:** compare the current CATSS corruption with upstream
   `CATSS_parsers.patch_parallel` and current parser continuation/provenance code.
2. **RED:** create synthetic seven-line regression for exact
   `02.Exodus.par` Exod 35:19 and verify it fails before production code.
   Assert one alignment, all seven raw physical lines and source-line numbers,
   no spurious verse or malformed continuation. Add different-book,
   different-reference and mutated-cell negative tests.
3. **Implementation:** add a closed raw-line window detector and a special
   layout-dummy path in `parse_parallel_text`. Do not globally relax header
   boundaries or continuation rules. Keep source-derived alignment IDs.
4. **GREEN:** focused and full offline tests (Python 3.11/3.12/3.13),
   lint/format/mypy, and opt-in complete 46-file parser audit. Add an exact
   complete-source CI guard against the upstream line sequence and preservation
   of each physical line.
5. **Independent adversarial review:** inspect actual CCAT evidence,
   upstream patch, exact production diff, near-miss input, provenance,
   verse accounting and the CI logs at the final head. Revisit RED on
   any behavioral review finding. Merge only reviewed exact-head GREEN.
