# Plan — issue #81 exact missing-minus repair

Research basis: [issue-81-missing-minus-1kings.md](../research/issue-81-missing-minus-1kings.md).

## Gate 1 — RED tests

Before production changes require the exact 1/3 Kgs 22:50 row to:

1. preserve raw `)X)B -> [16.28g]`;
2. preserve its contextual-reference annotation/payload;
3. become semantically Greek-side LXX-minus;
4. derive technique-v1 omission and not addition;
5. emit exactly one LXX-side `source_repair` annotation with payload
   `--- [16.28g]`;
6. preserve the source-derived alignment id;
7. leave the same cells at another reference unrepaired.

Commit and confirm semantic RED before implementation.

## Gate 2 — implementation

Add one entry to the existing closed LXX-side source repair table:

`("13.1Kings.par", 22, 50, ")X)B", "[16.28g]") -> "--- [16.28g]"`.

No generic marker, reference, lexical-count or technique logic changes.

## Gate 3 — complete-snapshot guard

Across the live 46-file snapshot require exactly this repaired identity and verify:

- raw Greek remains `[16.28g]`;
- semantic LXX-minus is true;
- contextual reference `16.28g` survives;
- technique omission is true;
- no other reference-only row is classified via this repair.

## Gate 4 — exact-head GREEN and independent review

Require Python 3.11/3.12/3.13, ruff, format, mypy, release smoke and complete snapshot
on the exact final SHA.

Review independently for accidental generic reference-only minus semantics, provenance
drift, payload loss, identity over-broadening and regression of earlier LXX-side
source repairs.
