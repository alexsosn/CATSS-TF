# Research — issue #50 MT-column `---` apparent minus

## Scope

Issue #50 was discovered by the complete-CATSS gate for the standalone canonical corpus.
The first blocking row is under the current CATSS source header **Genesis 8:7**:

```
--- =;L/R)T <8.8>	TOU= I)DEI=N
```

The `<8.8>` text belongs to source-note/retroversion markup; it is not the CATSS
header reference.

The current parser already derives zero MT lexical elements, two Greek lexical
elements, and a column-B contextual retroversion. It lacks a typed semantic for the
MT-column-A `---` marker, so technique-v1 rejects the otherwise explicit CATSS event.

## Documentary/prior-parser evidence

Cody Kingham's open CATSS parser reconstruction explicitly separates two Hebrew-side
alignment markers in `regex_patterns.py`:

- `--+`: “In column A of the Hebrew: element added in the Greek”;
- `---`: “apparent minus in the MT over against the Greek”.

His accompanying research notes, based on the CATSS 1986/1991 documentation, describe
Hebrew column A as the formal MT-equivalent column and column B as selected
retroverted/reconstructed Hebrew readings presumed behind the Greek.

The categories therefore must not be collapsed. `--+` is explicit source evidence for
an addition in Greek relative to MT. Hebrew-side `---` is evidence that MT apparently
lacks an element represented by Greek, potentially accompanied by a reconstructed
Hebrew Vorlage in column B.

A separate current parser, `curran-gehring/catss`, likewise treats `--+` in Hebrew as
LXX-plus and Greek-side `---` as LXX-minus. It does not model Hebrew-side `---`
separately, so it supplies no basis for treating the two Hebrew markers as synonyms.

## Existing CATSS-TF vocabulary

`notation.py` already declares the semantic identity:

```
Ap- -> apparent_minus (family: alignment)
```

The generic TF schema therefore already defines
`catss_sem_apparent_minus*` features. The parser should emit that existing semantic
identity rather than creating a synonym.

CATSS-TF already admits zero-side transposition carriers without classifying them as
translation additions/omissions. Apparent MT minus should use the same conservative
principle: it is explicit evidence that makes the zero-MT shape valid, while
`addition_vs_mt` remains false.

## Complete 46-file snapshot audit

A research-only CI scan loaded all 46 current CATSS parallel files:

- 26,183 verse records;
- 349,908 alignment records;
- 350,426 accounted source data lines;
- zero unaccounted lines;
- zero unknown semantic annotations.

For every Hebrew-empty / Greek-nonempty alignment, the audit grouped the first
MT-column-A marker:

| marker class | count | interpretation/status |
| --- | ---: | --- |
| `--+` | 19,943 | explicit LXX-plus, already modeled |
| `-+` | 4 | explicit plus variant, already modeled |
| `---+` | 12 | explicit plus variant, already modeled |
| `{...}` | 6,220 | remote transposition, already modeled |
| `^` | 468 | transposition evidence, already modeled |
| `^^^` | 397 | transposition evidence, already modeled |
| `---` | **61** | zero-MT/nonempty-Greek apparent-minus technique class; scope of #50 |
| Sirach `[..]` | 4,278 | manuscript/witness lacuna; split to #52 |
| raw-empty / column-B-only | 13 | heterogeneous residual set; split to #53 |
| MT-side `--` | 4 | unresolved residual set; split to #53 |
| other stylistic-transposition brace forms | 8 | already typed transposition evidence |

Representative `---` rows occur across multiple books and include forms with ditto
marks, column-B retroversions, contextual references, and occasional independent
transposition annotations. A second marker-wide audit found **63** alignments whose
MT-column-A first token is exactly `---`. Their cardinalities are:

- `(0, 1)`: 40;
- `(0, 2)`: 17;
- `(0, 3)`: 4;
- `(0, 0)`: 1;
- `(1, 2)`: 1.

Thus the homogeneous technique class in #50 is the 61 zero-MT/nonempty-Greek rows.
The marker itself is still typed as `apparent_minus` on all 63 rows, but the two
contradictory-cardinality outliers remain fail-closed and are tracked separately in
#54. The population supports a documented marker rule without implying that every
surface occurrence has a valid technique-v1 cardinality.

## Representation decisions

### R50-1 — parser semantic

When the **first token of MT column A is exactly `---`**, emit one
`Annotation(side="mt_a", kind="apparent_minus", family="alignment", raw="---")`.

Do not set `is_lxx_plus`. Do not infer this semantic from lexical emptiness alone.
Greek-side `---` continues to mean `is_lxx_minus` and must not emit the MT
`apparent_minus` semantic.

### R50-2 — technique admissibility

Technique-v1 accepts a Hebrew-empty / Greek-nonempty alignment when explicit
MT-apparent-minus evidence is present, in addition to the already accepted LXX-plus and
transposition cases.

For this class:

- cardinality remains `zero_one` / `zero_many`;
- token balance remains `not_applicable`;
- `addition_vs_mt=False`;
- `omission_vs_mt=False`;
- transposition remains independently derived.

Technique validation rejects contradictory `apparent_minus` evidence if MT lexical
material is present or Greek lexical material is absent.

### R50-3 — projection representation

On `catss-lxx`, the existing Greek word memberships carry
`catss_sem_apparent_minus=1` and
`catss_sem_apparent_minus_mt_a=1`. This requires the semantic to cross the projection
boundary while retaining its source scope, analogous to the existing explicit
`source_repair` provenance rule.

On `catss-bhsa`, no MT word exists for the event. The resolver emits a distinct
verse-level anchor kind `apparent_mt_minus`. TF exposes both an aggregate
`catss_apparent_mt_minus_n` and `catss_sem_apparent_minus=1` on the BHSA verse node.
The anchor sidecar preserves each individual alignment identity and Greek token count.

The existing `lxx_plus` anchor remains separate.

### R50-4 — canonical representation

The standalone canonical corpus needs no special node type: its alignment slot already
survives zero lexical elements, and its first-class annotation node preserves
`apparent_minus` with `mt_a` scope. Once #50 lands on main, #40's complete-corpus
gate exercises this path.

### R50-5 — cross-projection consistency

For sources supported by both projections, apparent MT minus is an expected asymmetric
shape:

- canonical alignment/annotation/technique rows remain identical in both bundles;
- BHSA has no word mapping for the alignment and carries one
  `apparent_mt_minus` verse anchor;
- LXX carries complete `lxx_i` word mappings and no structural anchor.

The consistency checker must classify this shape from the typed
`Annotation(side="mt_a", kind="apparent_minus")`, not from zero-MT counts alone.

### R50-6 — residual classes stay separate

The audit discovered materially different zero-MT classes. They are not part of #50:

- #52: Sirach `[..]` witness lacuna/illegibility;
- #53: 13 raw-empty/column-B-only rows plus four MT-side `--` rows requiring
  source-by-source forensic classification;
- #54: the two MT-side `---` outliers with cardinalities `(0, 0)` and `(1, 2)`.

No generic “empty MT is acceptable” fallback is permitted. #50 deliberately keeps
those two anomalous `---` rows contradictory in technique-v1 until their source
contexts are researched.
