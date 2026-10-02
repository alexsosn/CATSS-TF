# Research — issue #54 apparent-minus cardinality outliers

## Scope

The complete 46-file audit behind #50 found 63 alignments whose MT-column-A first
token is exactly `---`.

The population is:

- 61 ordinary apparent-MT-minus rows with `mt_n == 0` and `lxx_n > 0`;
- one zero/zero outlier;
- one mixed lexical outlier with `(mt_n, lxx_n) == (1, 2)`.

The 61 homogeneous rows remain governed by the strict apparent-minus technique
invariant implemented by #51.

## Outlier A — 1 Esdras 4:28 marker-only long-minus/plus row

Exact current source state:

- source: `17.1Esdras.par`;
- reference: 1Esdr 4:28;
- historical audit source line: 2173;
- raw row: `--- ''\t--+`;
- MT tokens: none;
- Greek tokens: none;
- no transposition evidence.

Immediate current-source context ends a sequence of Greek-addition rows:

```
--+ ''    AI( XW=RAI
--+ ''    EU)LABOU=NTAI
--+ ''    A(/YASQAI
--+ ''    AU)TOU=
--- ''    --+
```

The CATSS manual resolves an earlier ambiguity in our working notes:

- `''` means **long minus or plus (at least four lines)**;
- modern documentation spells `--- ''` as long minus and `--+ ''` as long plus;
- `--- {x}` / `--+ {x}` are a separate apparent-minus/apparent-plus category for
  lack of equivalence over long stretches.

Therefore `''` is not a generic column/ditto marker. The zero/zero row occurs at a
boundary/interaction inside a documented long plus/minus structure. The Greek-side
`--+` remains anomalous and must not be interpreted from spelling alone.

Follow-up: #86 researches the exact long-block semantics and source boundary before any
behavior change.

## Outlier B — Jonah 4:3 mixed apparent-minus + lexical row

Exact current source state:

- source: `32.Jonah.par`;
- reference: Jonah 4:3;
- raw row: `--- YHWH\tDE/SPOTA KU/RIE`;
- MT lexical tokens: `YHWH`;
- Greek lexical tokens: `DE/SPOTA`, `KU/RIE`;
- typed leading MT-side `apparent_minus`;
- no transposition evidence.

Current CATSS confirms this is one physical/logical row, not a continuation or
column-splitting defect. The prior open parser recognizes the leading `---`
independently from the following lexical `YHWH`.

Independent textual evidence matches that formal structure: Jonah 4:3 has MT יהוה
against Greek δέσποτα κύριε, and published discussion of the divine-name rendering
explicitly notes that the Greek has two titles where MT has only the tetragram.

The source therefore encodes two element-level facts in one row:

1. an apparent MT-minus counterpart for Greek `DE/SPOTA`;
2. ordinary lexical `YHWH -> KU/RIE`.

The whole row must not be forced into the pure apparent-minus cardinality class.

Follow-up: #85 models the scope at element level, grounded in the configured LXX parent
and canonical TF element/annotation nodes.

## Decision R54-1 — the outliers are heterogeneous

The two rows have different source grammars and cannot share a permissive technique
exception.

The strict rule for the 61 ordinary apparent-minus rows remains:

- zero MT lexical elements;
- one or more Greek lexical elements;
- no translation-addition/omission claim.

## Decision R54-2 — close research, split implementation

No production code belongs in #54.

Implementation/research continues independently:

- #85 — mixed Jonah 4:3 element-level apparent-minus scope;
- #86 — 1 Esdras 4:28 long-minus/long-plus boundary.

Any behavior change in those tickets follows research → plan → RED-first TDD →
implementation → exact-head GREEN → independent adversarial review.
