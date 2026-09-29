# Research — issue #64 residual Greek-empty alignments

## Trigger

Canonical corpus materialization on #47 now reaches a new fail-closed boundary after
#57 and #58: an alignment in `01.Genesis.par` with lexical MT material, no Greek
lexical tokens, and raw Greek `--+`.

Technique-v1 correctly refuses to infer omission semantics from cardinality alone.
The marker spelling is especially unsafe here because `--+` is documented as a
Hebrew-column LXX-plus marker; a Greek-column occurrence cannot inherit that meaning
without evidence.

## Research questions

1. How many current alignments have `mt_count > 0`, `lxx_count == 0`, are not
   already `is_lxx_minus`, and carry no transposition evidence?
2. What raw Greek-side forms account for them?
3. Are they isolated source anomalies, systematic legacy spellings, continuation
   artifacts, or another documented category?
4. Do the classes differ enough to require separate implementation tickets?

## Gate

A temporary complete-snapshot audit enumerates every residual row with:

- source and verse header;
- physical source lines;
- raw MT and Greek cells;
- first Greek-side token;
- MT/LXX counts;
- typed annotations and transposition flags;
- immediately neighboring alignment raw cells within the same verse.

No production semantics are changed during this research phase. The audit must remain
descriptive; any behavior change follows a separate plan and RED-first implementation.
