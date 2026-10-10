# Research — issue #60 two physically empty MT cells

## Current source-grounded baseline

Issue #53's complete 46-file scan isolated **exactly two** rows with an
*empty physical Hebrew column A*, no column-B reconstruction and nonempty
Greek lexical material, without a continuation diagnostic:

- `17.1Esdras.par`, 1 Esdr 4:25: empty MT cell against `GUNAI=KA`.
  This follows other explicit long Greek-plus material.
- `27.Sirach.par`, Sir 19:14: empty MT cell against `E)/LEGCON`.
  This precedes other rows marked with the explicit Hebrew-witness
  lacuna `[..]` siglum.

There is **no typed LXX-plus or manuscript-lacuna marker in the empty cell**.
Issue #52, now merged, deliberately admits Sirach witness lacuna only
when **the first token of MT column A is `[..]`**, with a typed MT-A
annotation. This physically empty Sirach row does not satisfy it. Source
shape is not sufficient to assign either translation-addition or
manuscript-absence semantics.

## Actual 46-file CCAT audit — R60-1

Exact source evidence was collected through the real parser and
`complete-catss-audit` at
[CI run 38094212475](https://github.com/alexsosn/CATSS-TF/actions/runs/38094212475)
(job 114336642798, commit `c60fbc5a42dfbaf0a1a12dfe42392c2b32d43d02`).
All five checks passed. The temporary structural logging step was
removed after the evidence was captured; **no source texts were
committed**.

| property | 1 Esdras 4:25 | Sirach 19:14 |
| --- | --- | --- |
| Source line | 2136 | 5877 |
| Alignment identity | `catss:17.1Esdras.par:b70bd8574763949dd489` | `catss:27.Sirach.par:74ae29b6b65d38cfba56` |
| Hebrew MT column A | physically empty | physically empty |
| Hebrew column B | absent | absent |
| Greek lexical elements | 1 | 1 |
| Typed source annotations | none | none |
| LXX plus/minus flag | neither | neither |
| Transposition flags | all false | all false |
| Leading/trailing continuation | neither | neither |

### 1 Esdras: isolated missing siglum within explicit plus block

Four preceding alignments (source lines 2132–2135) all have explicit
MT-A first marker `--+`, with Greek lexical element counts
(2, 1, 1, 2); three following alignments (2137–2139) again start
`--+`, with counts (1, 3, 3). The intervening row at line 2136
has **no** Hebrew-side marker or annotation. A missing/export-lost
`--+` is plausible from its neighborhood, but is **not documentary
evidence that the current row was intentionally classified as a plus**.
There is no `#` continuation chain that would prove the row simply
belongs to its neighbor.

### Sirach: blank at beginning of witness-lacuna sequence

At the same chapter/verse (Sir 19:14), line 5877 is an entirely blank
MT cell without a `[..]` annotation, while the next six
alignments (lines 5878–5883) explicitly begin `[..]` and each has
the correctly scoped `sirach_lacuna_or_illegible` annotation. They
contain Greek lexical element counts (2, 1, 1, 1, 2, 1). The empty
first line may represent missing witness sigla, but unlike its
successors carries **no positive witness-lacuna evidence**. The #52
rule must not be applied by neighborhood inheritance.

## Research disposition — R60-2

**Keep both rows unclassified; do not introduce any technique rule.**
Their different neighboring markers are evidence against treating
physical Hebrew emptiness as a single semantic class. The actual
canonical corpus still has **31 unclassified technique alignments**
and **349,670 alignment slots** after #52, as verified in the same
run, with successful Text-Fabric readback.

Further adjudication needs an authoritative 1991 CCAT source/export
copy or documented editorial convention specific to these records,
ideally alongside the relevant 1 Esdras and Ben Sira textual witness
evidence. The existing #60 remains open; no new behavior ticket is
justified until the source notation itself is established. Preserve
the exact spellings, IDs and absence of metadata. Reject generic
zero-MT inference, reconstructed Hebrew, fake Greek word targets or
borrowed sigla. If upstream evidence later establishes a correction,
use a separate research → plan → RED → GREEN → adversarial-review gate.
