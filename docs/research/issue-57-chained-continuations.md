# Research — issue #57 chained physical CATSS continuations

## Scope

The complete-snapshot forensic audit in #53 found five apparent Hebrew-empty /
Greek-nonempty alignments that are parser artifacts rather than semantic alignment
events. Each is a physical source line beginning with `#` that belongs to the
immediately preceding logical CATSS alignment.

Current examples:

- `06.JoshB.par`, JoshB 9:5, line 3752;
- `13.1Kings.par`, 1/3 Kgs 20:33, line 14622;
- `27.Sirach.par`, Sir 12:4, lines 3694 and 3696;
- `45.DanielOG.par`, Dan 1:5, line 85.

The current parser joins a continuation only while the *previous* physical row ends
with `#`. It flushes as soon as the first continuation fragment lacks a trailing
`#`, so a subsequent row beginning with `#` is emitted as a separate alignment
and diagnosed `malformed_continuation`.

## CATSS continuation evidence

Cody Kingham's research notes reconstruct the CATSS 1986/1991 physical-line convention:

- a long logical line may be broken with `#`;
- the first physical fragment has `#` at the end;
- the continuation physical line has `#` in the opposite column at the beginning;
- the fragments are to be recombined into one logical alignment.

Example from Genesis 15:11 in the notes:

```
H/PGRYM    TA\ SW/MATA {d} TA\ DIXOTOMH/MATA #
#          AU)TW=N
```

The same notes describe export corruption and orphaned physical fragments in multiple
books, confirming that physical-line boundaries are not alignment boundaries.

The five current #53 cases add one detail: a logical alignment may need more than two
physical fragments. A middle fragment can begin with `#` but not itself end in
`#`; the following fragment's leading `#` is still explicit continuation evidence.
Therefore continuation membership cannot be decided solely from
`pending[-1].continues`.

## Current parser failure

`parse_parallel_text()` currently:

1. appends a physical row when the pending row ends with `#`;
2. immediately flushes if the newly appended row does not itself end in `#`;
3. on the next physical row, a leading `#` has no pending logical alignment and is
   classified `malformed_continuation`.

This creates a false extra alignment, false zero-MT semantics, and a spurious diagnostic.

## Decision R57-1 — leading hash is positive continuation evidence

Within one verse, an incoming physical row whose parsed cell begins with the standalone
continuation marker `#` belongs to the immediately preceding pending logical
alignment, even if that preceding physical fragment did not end with `#`.

Conversely, a trailing `#` on the previous fragment continues to require the next
data row to join, preserving existing behavior.

## Decision R57-2 — defer ordinary-row flush by one data-row boundary

The parser must retain the current pending logical row until it sees the next data row
or verse boundary. On the next data row:

- append when the previous fragment ends with `#`;
- append when the incoming fragment begins with `#`;
- otherwise flush the pending logical alignment and start a new one.

A verse header or EOF flushes pending first, so a leading-`#` fragment can never attach
across verse boundaries.

## Decision R57-3 — provenance remains physical

Joining fragments changes logical grouping only:

- `source_lines` contains every original physical line number in order;
- `raw_lines` contains every original physical line verbatim;
- `catss_alignment_id` derives from the complete original fragment sequence;
- MT/LXX lexical cells concatenate using the existing continuation-cell join logic;
- each physical data line remains accounted for exactly once.

## Decision R57-4 — malformed continuation remains fail-closed

A leading-`#` physical row with no preceding pending alignment in the same verse is
still diagnosed `malformed_continuation`. A logical alignment that ends at a verse
boundary/EOF with a trailing `#` is still diagnosed likewise.

The change must not turn arbitrary orphan lines into silent continuations.

## Complete-snapshot acceptance

After implementation, the five known false residual alignments disappear as separate
alignments and their physical lines become members of the preceding logical alignments.
The complete parser audit must still report:

- all 46 source files;
- zero unaccounted data lines;
- zero unknown annotations.

A focused snapshot guard should assert that the five exact physical lines no longer
appear as standalone alignment starts and no longer produce
`malformed_continuation` diagnostics.
