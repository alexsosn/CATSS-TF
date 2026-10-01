# Plan — issue #66 CATSS export-orphan physical lines

Research basis: [issue-66-orphan-lines.md](../research/issue-66-orphan-lines.md).

## Gate 1 — RED tests

Add tests before production changes for:

1. a non-Psalms no-tab fragment joining the preceding Greek cell inside a token;
2. preservation of a real source whitespace boundary when the orphan starts a new
   Greek token;
3. a Psalms no-tab fragment joining the beginning of the following Hebrew cell;
4. consecutive Psalms fragments joining in source order before the following Hebrew
   row (the Ps 68:31 shape);
5. repaired alignments preserving every original `source_line`, `raw_line`, and an
   alignment id derived from the complete physical sequence;
6. no `unsplit_row` diagnostic after a successful layout repair;
7. fail-closed behavior when the required directional neighbor is absent at a verse
   boundary;
8. all four exact Joshua B layout repairs, including the JoshB 4:11 continuation;
9. existing `#` continuation tests remaining unchanged.

The RED commit changes tests/guards only.

## Gate 2 — implementation

Introduce a source-layout repair layer inside the parser, before semantic alignment
interpretation.

### Exact Joshua B repairs

Use a closed mapping keyed by source, chapter, verse and exact outer-trimmed raw
physical text to restore MT/LXX cells for the four researched whole-row corruptions.
The physical `raw` string and line number remain unchanged.

### Generic non-Psalms orphan

When a no-tab row is encountered and a preceding logical row exists in the same verse,
append the orphan's raw fragment exactly to the preceding Greek cell. Preserve any
whitespace already present at the original Greek-cell boundary; do not synthesize a
separator. Keep the orphan physical row in the logical alignment solely for provenance.

### Generic Psalms orphan

Hold one or more no-tab fragments until the following split row in the same verse,
then prepend their raw strings exactly to that row's Hebrew cell. Preserve physical
source order and allow the repaired target row's normal `#` continuation behavior to
continue.

If the required neighbor is absent, do not repair: retain `column_split=False` and the
existing `unsplit_row` diagnostic.

No addition/omission/transposition semantic is created by layout repair.

## Gate 3 — complete-snapshot guard

On all 46 current files require:

- the same 208 physical no-tab source lines are still present in provenance;
- all 208 belong to successfully reconstructed logical alignments;
- zero final alignments have `column_split=False`;
- zero `unsplit_row` diagnostics;
- every physical data line remains accounted for exactly once;
- the existing continuation, apparent-minus, double-dash-repair and notation gates
  remain green.

## Gate 4 — exact-head verification

Run ruff, format, mypy, pytest on Python 3.11/3.12/3.13, release smoke, and complete
46-file audit on the exact implementation head.

## Gate 5 — logically independent adversarial review

Review the exact green head trying to falsify:

- accidental merging of a full corrupt row into a neighbor;
- invented whitespace at fragment boundaries;
- wrong repair direction in Psalms;
- crossing verse headers;
- loss/duplication/reordering of physical provenance;
- changed `#` continuation behavior;
- false disappearance of unresolved unsplit rows;
- interaction with existing exact source repairs.

Any blocker returns to RED → implementation → full exact-head verification.
