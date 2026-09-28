# Plan — issue #57 chained physical continuations

Research basis: [issue-57-chained-continuations.md](../research/issue-57-chained-continuations.md).

## Gate 1 — RED tests

Commit failing tests before production changes:

1. three-fragment Greek continuation where fragment 1 ends with `#`, fragments 2 and
   3 begin with `#`, and fragment 2 has no trailing `#`: all three physical lines
   form one logical alignment;
2. `source_lines`, `raw_lines`, lexical token order and source-derived alignment id
   include all three fragments;
3. no `malformed_continuation` diagnostic is emitted for the valid chain;
4. a leading-`#` row at the start of a verse remains malformed and cannot attach
   across a verse header;
5. existing ordinary adjacent rows remain separate;
6. existing two-fragment continuation remains unchanged.

## Gate 2 — implementation

Refactor only the pending-row state transition in `parse_parallel_text()`:

- keep a pending logical alignment until the next data row/header/EOF;
- append an incoming row when either the previous row trails `#` or the incoming row
  leads with `#`;
- otherwise flush then start the incoming row;
- preserve current `flush_pending()` malformed trailing-continuation check.

Do not add source-specific repairs or zero-side technique exceptions.

## Gate 3 — complete-snapshot guard

Assert the five researched source-line identities are incorporated into multi-line
alignments and are absent from `malformed_continuation` diagnostics.

Retain the complete notation/accounting audit.

## Gate 4 — GREEN and review

Run Python 3.11/3.12/3.13, ruff, format, mypy, pytest, release smoke and the complete
46-file audit on the exact final head.

Then perform logically independent adversarial review focused on:

- accidental merging of ordinary adjacent alignments;
- attachment across verse headers;
- duplicate/lost physical source lines;
- changed two-line continuation behavior;
- incorrect MT/LXX-side concatenation;
- alignment-ID instability unrelated to the corrected grouping.

Merge only after exact-head GREEN and no blocking findings.
