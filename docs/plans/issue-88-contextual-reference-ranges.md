# Plan — issue #88 contextual-reference ranges

Research basis: [issue-88-contextual-reference-ranges.md](../research/issue-88-contextual-reference-ranges.md).

## Pinned-parent discovery (issue #91)

The exact LXX release has **no distinct Josh 9:2a–f subverse nodes**. Gate 5 below
is intentionally fail-closed, and Gate 6 canonical TF preservation is mandatory.
Do not treat six synthetically resolvable fake-provider spans as evidence that
six real parent nodes exist. The module supports range membership conditionally
for future verified parent editions but cannot export this specific JoshB range
against the current pinned LXX.


## Gate 1 — RED parser/IR tests

Before production changes, add focused tests for the exact source row:

```
JoshB 9:2
{...} <8.30-35>\t[[9.2a-2f]]
```

Require:

1. raw line, MT/LXX raw cells and stable alignment id remain unchanged;
2. lexical counts remain `(0, 0)`;
3. existing MT `transposition_remote` / `{...}` annotation survives;
4. `<8.30-35>` survives with its existing contextual note payload;
5. Greek contextual-reference annotation/raw payload survives;
6. one typed `GreekReferenceRange` is produced with start 9:2a and end 9:2f;
7. no scalar `GreekReference` is fabricated from either endpoint;
8. `invalid_lxx_reference` disappears for this valid range;
9. malformed/reversed variants remain fail-closed diagnostics.

Commit and observe semantic RED before parser implementation.

## Gate 2 — parser implementation

Add the dedicated range type and a closed range parser for the observed CATSS grammar.

Do not change scalar `GreekReference` semantics or the generic multiple-reference
failure rule.

## Gate 3 — RED resolver/module tests

Add a parent fixture with six subverse spans a–f and require the structural range row to:

- resolve all six spans inclusively and in order;
- produce no lexical word mappings;
- preserve one alignment identity across six range members;
- expose member ordinal/count and range endpoint metadata;
- fail closed if one member is absent;
- leave ordinary scalar-reference and transposition-anchor tests unchanged.

Add a BHSA regression proving the duplicate structural `JoshB 9:2` record is not fed
into ordinary zero-vs-lexical word-count comparison.

Observe RED before resolver/schema implementation.

## Gate 4 — projection implementation

Introduce a dedicated range-membership result/event rather than abusing the
single-anchor identity contract.

For the LXX TF module, attach sparse query-native range features to the six existing
parent subverse nodes. At minimum the per-node representation must make the following
recoverable without sidecar interpretation:

- CATSS alignment identity;
- range raw spelling;
- member ordinal;
- member count;
- start chapter/verse/subverse;
- end chapter/verse/subverse.

Audit the complete snapshot for concurrent range memberships before choosing a scalar
lane count; do not silently overwrite collisions.

## Gate 5 — exact pinned-parent / complete-snapshot guard

In CI, acquire the exact configured CATSS snapshot and
`CenterBLC/LXX@f32a98eddf7eb239aa73ab863d70381e416d5076`.

Assert:

- the exact JoshB range row occurs once;
- it parses as one range 9:2a–9:2f;
- pinned-parent Josh 9:2 has exactly one unlabeled subverse node 630920 spanning 191 words;
- all six requested labeled targets a–f are absent in this release;
- the LXX resolver returns `missing_lxx_reference_range_member` and **zero** range memberships;
- the LXX materializer fails closed, publishing no module for that unsupported range;
- synthetic parent fixtures with explicit a–f nodes still produce six correct ordered memberships;
- no fabricated parent node/word is used;
- the complete parser snapshot has no `invalid_lxx_reference` caused by this range;
- no new unresolved diagnostics are introduced;
- ordinary scalar reference counts/semantics remain stable.

## Gate 6 — canonical-corpus integration

Update PR #47, or its successor if #40 lands first, so canonical materialization represents
`lxx_reference_ranges` as first-class nodes with start/end features and raw provenance.
Do not collapse ranges to scalar references.

This is an integration dependency, not permission for a TF module to create nodes.

## Gate 7 — exact-head GREEN and independent adversarial review

Require Python 3.11/3.12/3.13, ruff, format, mypy, release smoke, complete CATSS audit
and pinned-parent guard on the exact final SHA.

Then perform a logically independent review grounded in:

- the real JoshB source neighbourhood 8:30–9:3;
- range grammar boundaries;
- pinned LXX subverse structure;
- BHSA duplicate-header behavior;
- TF module no-new-nodes rule;
- canonical-corpus preservation contract;
- regressions in ordinary scalar references.

Any blocker returns to the appropriate RED → implementation gate.
