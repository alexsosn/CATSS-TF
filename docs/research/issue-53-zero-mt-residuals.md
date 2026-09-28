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
