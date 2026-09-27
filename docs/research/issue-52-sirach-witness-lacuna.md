# Research — issue #52 Sirach Hebrew-witness lacunae

## Scope

The complete 46-file CATSS audit performed for issue #50 found **4,278**
Hebrew-empty / Greek-nonempty alignments in `27.Sirach.par` whose MT-side
first marker is `[..]`.

These alignments currently parse with zero MT lexical elements and nonzero Greek
material. Technique-v1 rejects that cardinality unless the alignment is explicit
LXX-plus or transposition evidence. That would be the wrong interpretation for
Sirach witness lacunae.

## Documentary and prior-parser evidence

Cody Kingham's reconstruction of the CATSS 1986/1991 documentation records an
outdated/actual-siglum correspondence:

```
docs {..}  ->  actual [..]  = "lacuna in [manuscript]" (1991:123)
```

His parser patterns classify `[..]` as `lac` with the description
“lacuna reflected in manuscript of extrabiblical passage”. Related patterns
record a lacuna in a specifically listed manuscript.

The same repository contains a Sirach-specific source repair normalizing one
old `{..}` occurrence in `27.Sirach.par` to the current `[..]` spelling.
This corroborates that `[..]` is manuscript-state evidence in the received
Sirach data, not an LXX-addition marker.

Therefore an empty Hebrew side caused by `[..]` means that the Hebrew witness
is lacunose/illegible at the aligned location. It does not by itself assert that
the Greek translator added material relative to a recoverable Hebrew Vorlage.

## Existing CATSS-TF semantics

CATSS-TF already has a Sirach-sensitive notation catalogue:

```
[..] -> sirach_lacuna_or_illegible
family = sirach_manuscript
```

The parser already emits that typed annotation on the source side. Its lexical
preparation treats the siglum as non-lexical, so a row such as:

```
[..]\tPA=SA
```

correctly has `mt_count == 0` while retaining the manuscript annotation.

No new notation identity is needed.

## Parent/projection coverage

`27.Sirach.par` is explicitly **unsupported** by the BHSA projection because
BHSA has no Ben Sira parent book.

It is explicitly **supported** by the CenterBLC/LXX projection:

```
27.Sirach -> Sir
```

Consequences:

- there is no faithful BHSA word or verse anchor to create for these events;
- canonical CATSS can retain the alignment slot and first-class manuscript
  annotation directly;
- the LXX projection can map the existing Greek words and should carry the
  MT-scoped `sirach_lacuna_or_illegible` semantic onto those Greek memberships
  while preserving source scope `mt_a`.

This is projection of source evidence, not a claim that the Greek word itself is
lacunose.

## Technique interpretation

Technique-v1 should admit Hebrew-empty / Greek-nonempty cardinality when the
alignment carries explicit MT-side `sirach_lacuna_or_illegible` evidence.

For such an alignment:

- cardinality remains `zero_one` / `zero_many`;
- token balance remains `not_applicable`;
- `addition_vs_mt=False`;
- `omission_vs_mt=False`;
- transposition evidence remains independently derived.

The evidence is manuscript availability, not translation expansion.

The admissibility rule must be derived from the typed annotation. It must not
generalize to all Sirach rows, all square-bracket syntax, or all zero-MT rows.

## Complete-snapshot evidence

Issue #50's research-only complete snapshot audit found:

- 4,278 Hebrew-empty / Greek-nonempty alignments whose first MT-side marker is
  `[..]`;
- all belong to `27.Sirach.par`;
- representative rows begin at Sirach 1:1 and contain ordinary Greek lexical
  material;
- the parser already reports `sirach_lacuna_or_illegible` on those rows;
- this population is materially distinct from explicit LXX-plus, MT apparent
  minus, transpositions, and the heterogeneous residual set tracked in #53.

A permanent acceptance guard should verify the complete current snapshot
population rather than silently broadening the technique rule.

## Decisions

### R52-1 — reuse the existing manuscript semantic

Do not introduce a new feature name. Technique evidence is the exact typed
annotation:

```
side == "mt_a"
kind == "sirach_lacuna_or_illegible"
family == "sirach_manuscript"
```

### R52-2 — preserve translation-technique neutrality

This evidence makes the zero-MT shape admissible but never sets
`addition_vs_mt` or `omission_vs_mt`.

Contradictory use with a nonempty MT lexical side or an empty Greek lexical side
must fail closed in the technique layer.

### R52-3 — LXX projection carries MT-scoped witness evidence

For mapped Sirach Greek word nodes expose:

- `catss_sem_sirach_lacuna_or_illegible=1`;
- `catss_sem_sirach_lacuna_or_illegible_mt_a=1`.

The semantic may cross from MT source scope to the LXX projection only for this
documented witness-lacuna kind; retain the original `mt_a` scope.

### R52-4 — no BHSA representation

Because Sirach is declared unsupported on BHSA, do not invent a BHSA structural
anchor or relax source classification.

### R52-5 — residual empty-MT classes remain outside this ticket

Issue #53 continues to own raw-empty/column-B-only and MT-side `--` cases.
No generic “zero MT is acceptable” fallback is permitted.
