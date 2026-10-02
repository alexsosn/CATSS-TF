# Plan — issue #82 exact 1 Esdras Greek lexical repair

Research basis: [issue-82-missing-greek-1esdras.md](../research/issue-82-missing-greek-1esdras.md).

## Gate 1 — RED tests

Before production changes, require the exact 1 Esdras 6:4 row to:

1. preserve raw `L/KM -> [e5.3]` and physical source provenance;
2. preserve the typed `contextual_reference` annotation/payload `e5.3`;
3. expose semantic Greek token `U(MI=N`;
4. become lexical cardinality `(1,1)` with neither plus nor minus;
5. derive technique-v1 `one_one`, neither addition nor omission;
6. emit exactly one LXX-side `source_repair` annotation with payload
   `U(MI=N [e5.3]`;
7. preserve the source-derived alignment id;
8. leave the same cells at another reference unrepaired and fail closed;
9. resolve through `resolve_lxx_document()` with a parent span containing `ὑμῖν`
   to the exact word node, with no anchor or finding.

Commit the tests first and confirm semantic RED.

## Gate 2 — implementation

Add one closed entry to the existing LXX-side exact source-repair table:

`("17.1Esdras.par", 6, 4, "L/KM", "[e5.3]") -> "U(MI=N [e5.3]"`.

Do not change:

- generic reference parsing;
- Greek lexical normalization;
- resolver placement rules;
- technique validation;
- source-repair identity matching.

## Gate 3 — permanent complete-snapshot / parent-grounded guard

Convert the temporary research step into an assertion that:

- the actual 46-file snapshot contains exactly one repaired
  `17.1Esdras.par / 6:4 / L/KM / [e5.3]` identity;
- raw source and contextual reference are preserved;
- semantic token is `U(MI=N`;
- technique is `one_one` with no addition/omission;
- the exact configured `CenterBLC/LXX@f32a98ed...` parent still contains exactly one
  normalized `U(MI=N` in `1Esdr 6:4`;
- production resolver maps the repaired row to node 294471;
- no reference anchor is emitted.

Any parent drift or new ambiguity fails the guard.

## Gate 4 — exact-head GREEN and independent adversarial review

Require Python 3.11/3.12/3.13, ruff, format, mypy, release smoke, full CATSS snapshot,
and pinned-parent mapping on the exact final SHA.

Then independently review for:

- over-broad contextual-reference repair;
- accidental lexical fabrication outside the exact identity;
- raw/provenance or alignment-id drift;
- loss of `[e5.3]`;
- wrong parent reference or token;
- ambiguous/fuzzy resolver placement;
- regression of #81 reference-only missing-minus repair.

Any blocker returns to RED → implementation → complete exact-head verification.
