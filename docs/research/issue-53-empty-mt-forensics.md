# Research — issue #53 residual Hebrew-empty alignments

## Scope

The complete 46-file audit performed while researching #50 isolated a residual
Hebrew-empty / Greek-nonempty population that is not explained by explicit LXX-plus,
transposition, Sirach witness lacunae, or the 61 admissible MT-apparent-minus rows.

The residual groups initially reported were:

- 13 raw-empty / column-B-only alignments;
- 4 alignments whose MT-column-A first token is `--`.

This ticket is forensic first. The examples are not semantically homogeneous.

## Cluster A — malformed physical continuation, not an empty-MT semantic

At least two of the 13 apparent raw-empty alignments are artifacts of the current
continuation parser.

### Joshua B 9:5

Current upstream context in `06.JoshB.par` is:

```
W/N(LWT    KAI\ TA\ KOI=LA #
#          TW=N U(PODHMA/TWN AU)TW=N {d}
#          KAI\ TA\ SANDA/LIA AU)TW=N
BLWT       PALAIA\
```

The second leading-`#` physical continuation is currently diagnosed as
`malformed_continuation` and becomes a separate Hebrew-empty alignment. The source
structure instead shows a multi-line Greek continuation of the preceding Hebrew row.

This is a parser/grouping problem. It must not be made technique-admissible as an
independent zero-MT alignment.

### 1 Kings 20:33

Current upstream `13.1Kings.par` contains:

```
H/M/M/NW   TO\N LO/GON # [21.33]
#          E)K TOU= STO/MATOS AU)TOU= [21.33]
W/Y)MRW    KAI\ EI)=PON [21.33]
```

The leading-`#` line is likewise reported by the current parser as
`malformed_continuation`. It belongs to the preceding logical alignment.

These two examples establish that the residual count cannot be solved by adding a
generic empty-MT technique exception.

## Cluster B — explicit column-B-only retroversion

Four residual rows occur consecutively in `12.2Sam.par`, 2 Samuel 15:18:

```
=;W/KL      KAI\ PA=S
=;H/KRTY    O( XEREQQI
=;W/KL      KAI\ PA=S
=;H/PLTY    O( FELEQQI
```

They are syntactically different from a blank MT cell:

- MT column A is empty;
- MT column B explicitly supplies a retroverted Hebrew form;
- Greek contains ordinary lexical material;
- the rows are not physical `#` continuations.

They follow a longer block of explicit `--+` retroversions in the same verse and
repeat Greek material corresponding to the Cherethites/Pelethites sequence.

CATSS documentation defines column B as selected reconstructed/retroverted Hebrew
readings presumed behind the Greek. Column-B presence is therefore positive source
evidence, but it is not automatically equivalent to `--+` and cannot be labeled a
translation addition without further documentation.

A dedicated inventory is required for all column-B-only residuals before defining a
technique rule.

## Cluster C — genuinely blank MT cells

The audit also found rows whose received MT cell contains only ditto/empty markup or
nothing lexical, for example:

- `06.JoshB.par` 9:5, which on inspection belongs to Cluster A;
- `13.1Kings.par` 20:33, which belongs to Cluster A;
- `17.1Esdras.par` 4:25 with Greek `GUNAI=KA`;
- additional rows not yet individually classified.

The remaining examples must be inspected one by one. Some may be continuation defects,
some may be edition/reference apparatus, and some may encode a documented empty-side
semantic.

## Cluster D — MT-side `--`

The audit found four MT-side `--` rows:

```
01.Genesis.par 22:16  --=;M/MN/Y <22.12> <sp>   DI' E)ME/
01.Genesis.par 48:13  -- =;)T/M <48.10>          AU)TOU\S
02.Exodus.par  10:24  --=;)LH/YKM <10.8>         TW=| QEW=| U(MW=N
15.1Chron.par  11:20  -- =B/P(M )XT              E)N KAIRW=| E(NI/
```

Current CATSS-TF treats `--` as a nonlexical alignment marker during MT tokenization,
but does not assign it an MT-side typed semantic. Cody Kingham's documented
apparent-MT-minus pattern is specifically `---`, not `--`.

These four rows therefore require source/documentation comparison before any semantic
alias is introduced. They must not be silently folded into #50.

## Current decisions

### R53-1 — no generic zero-MT fallback

Zero MT lexical count is an output shape, not source evidence. Technique remains
fail-closed until each residual class has an explicit semantic cause.

### R53-2 — split continuation repair from semantic modeling

Physical `#` continuation defects should be fixed in the shared parser with raw
physical-line provenance preserved and one stable logical alignment identity. A
continuation fix must be regression-tested independently of technique changes.

### R53-3 — column-B-only rows are a distinct research class

Do not relabel column-B-only retroversions as LXX-plus merely to satisfy technique-v1.
Determine the CATSS meaning of an absent column A with populated column B first.

### R53-4 — MT-side `--` remains unresolved

Do not treat `--` as an alias of `---` without documentary or current-source
evidence.

## Next research gate

Before planning implementation:

1. enumerate all 13 raw-empty/column-B-only residual alignments with exact source,
   reference, physical lines, raw cells, column-B state and parser diagnostics;
2. classify each as continuation artifact, column-B-only retroversion, apparatus, or
   other;
3. enumerate the four `--` rows with surrounding context and check prior CATSS
   patches/documentation;
4. split implementation tickets by cause if more than one parser/semantic fix is
   required.

Issue #54 separately owns the two contradictory-cardinality first-token `---`
outliers discovered after #50's marker-wide audit.
