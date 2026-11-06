# Research — issue #53 residual Hebrew-empty alignments

## Scope

The complete 46-file audit for #50 separated the documented zero-MT classes from a
small residual population that must not be accepted by shape alone:

- 13 raw-empty / column-B-only alignments;
- 4 alignments whose MT-column-A first token is `--`.

The canonical corpus gate in #40 now reaches one of these rows in Genesis:
`--=;M/MN/Y <22.12> <sp>\tDI' E)ME/`.

This ticket classifies every current occurrence before changing parser or technique
semantics.

## Constraints

- do not add a generic zero-MT escape hatch;
- preserve raw source bytes and stable alignment identities;
- distinguish parser structure defects, documented marker semantics and upstream
  corruption;
- compare each shape with CATSS documentation and prior parser/patch behavior where
  available;
- split implementation into separate issues/PRs if more than one cause is found;
- behavior changes require plan → RED-first TDD → implementation → exact-head GREEN →
  independent adversarial review.

## Research mechanism

A temporary CI-only complete-snapshot audit prints exact parser state plus local source
context for all 17 residual rows. No production code changes are made during this gate.


## Complete current-snapshot classification

The 46-file audit found exactly 17 residual alignments, in four structurally distinct
groups:

| class | count | current examples | interpretation status |
| --- | ---: | --- | --- |
| MT-column-A `--` + column B | 4 | Gen 22:16; Gen 48:13; Exod 10:24; 1 Chr 11:20 | undocumented/legacy marker form; requires separate semantic research |
| leading-`#` continuation fragments | 5 | JoshB 9:5; 1/3 Kgs 20:33; Sir 12:4 ×2; Dan 1:5 | parser grouping defect: fragments belong to an immediately preceding continued logical alignment |
| column-B-only reconstruction rows | 6 | 2 Sam 15:18 ×4; 1 Esdr 9:33; Ezek 4:5 | explicit reconstruction/translation-technique information with no col-A lexical item; not one safe category yet |
| physically empty MT cell, no continuation diagnostic | 2 | 1 Esdr 4:25; Sir 19:14 | isolated source/context cases; require source-specific classification |

The five continuation fragments all start with a physical leading `#` and occur
immediately after a logical row whose continuation chain has already begun. The current
parser flushes after the first continuation fragment whenever that intermediate physical
line lacks a trailing `#`, then reports the next leading-`#` fragment as
`malformed_continuation`. CATSS documentation and the prior parser research describe
`#` as physical line continuation markup; a leading `#` therefore carries structural
evidence that the physical line belongs to the preceding logical alignment. This is a
parser-structure bug, not zero-side technique semantics.

The four MT `--` rows all contain a column-B reconstruction and non-empty Greek, but
`--` is not the documented Hebrew-column LXX-plus marker (`--+`). They must remain
fail-closed until separately classified.

The six column-B-only rows are also not safe to infer as additions merely because
column A is empty. Their retroversion kinds include contextual, plain and vocalization
evidence and occur in different textual situations.

The two physically empty rows have no parser diagnostic and are not reducible to the
continuation bug. They remain source-specific research cases.

## Split decision

This umbrella issue should not acquire production behavior. Follow-up work is split
by cause:

- chained physical continuation parser defect;
- MT-side `--` marker semantics;
- column-B-only reconstruction carriers;
- isolated physically empty MT rows.

Each follow-up retains the normal research → plan → RED → implementation → exact-head
GREEN → independent review gates.
