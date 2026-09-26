# Issue 41 research — magical terminology case study

**Date:** 2026-09-26  
**Issue:** #41

## Scope

The case study will use Maria Yurovitskaya's 2018 Oxford seminar report
“Magic in Hebrew and Greek” as a compact scholarly question for demonstrating
how the two CATSS-TF projection modules can be queried together with their
parent corpora.

Primary source:

- Maria Yurovitskaya, “Magic in Hebrew and Greek,” in *Report of the Oxford
  Centre for Hebrew and Jewish Studies 2017–2018*, pp. 41–42:
  https://www.ochjs.ac.uk/wp-content/uploads/2019/02/ochjs-2018-pdf.pdf
- The associated seminar talk was advertised as “Greek magical terminology in
  the Septuagint”:
  https://www.hse.ru/data/2018/05/02/1151335642/OSAJS%20Septuagint.pdf

The report makes several kinds of claim that must be kept separate:

1. corpus-count/distribution claims, such as the distribution of `μάγος`;
2. Hebrew↔Greek translation-equivalent claims;
3. interpretive claims about semantic value or translator motivation;
4. external Greek-language-history claims that require evidence outside LXX/CATSS.

## Pinned corpus probe

The parent-corpus probe uses the exact LXX profile already frozen by CATSS-TF:

- repository: `CenterBLC/LXX`
- version: `1935`
- release: `v1.0.1`
- commit: `f32a98eddf7eb239aa73ab863d70381e416d5076`

Exact lemma counts in that parent at this commit:

| lemma | count | distribution |
| --- | ---: | --- |
| `μάγος` | 10 | Dan 2; DanTh 8 |
| `γόης` | 0 | — |
| `φαρμακός` | 13 | Exod 4; Deut 1; Ps 1; Mal 1; Jer 1; Dan 4; DanTh 1 |
| `φάρμακον` | 12 | 2Kgs 1; TobS 5; Wis 1; Sir 2; Mic 1; Nah 2 |
| `φαρμακία` | 8 | Exod 4; Wis 2; Isa 2 |
| `φαρμακεύω` | 3 | 2Chr 1; 2Mac 1; Ps 1 |
| `ἐπαοιδός` | 23 | Exod 5; Lev 3; 1Sam 1; 2Chr 1; Sir 1; Isa 1; Dan 4; DanTh 7 |
| `ἐπαοιδή` | 2 | Deut 1; Isa 1 |

Two scope effects are important enough to make central to the example.

### Daniel

A naive all-parent count gives ten occurrences of `μάγος`, but the parent keeps
Old Greek Daniel (`Dan`) and Theodotion (`DanTh`) separate. Old Greek Daniel
contains exactly two occurrences, at 2:2 and 2:10. Theodotion supplies eight
additional occurrences.

This explains how the report's statement that `μάγος` occurs twice in Daniel
can be recovered from the corpus without collapsing the two Daniel traditions.

### φάρμακον

Across the entire CenterBLC parent, `φάρμακον` occurs twelve times and is
evenly split between singular and plural forms (six each). The singular examples
are concentrated in Tobit S, Wisdom, and Sirach.

Restricting the question to books that project to BHSA changes the result:
2Kgs 9:22, Mic 5:11, and Nah 3:4 (two tokens) are all plural. The case study
must therefore state its corpus boundary before treating “only plural” as
confirmed or contradicted.

## CATSS alignment examples

The case study will show alignment-based examples, not verse-position guesses.
Representative CATSS rows include:

- Exod 7:11:
  - `W/L/MK$PYM` ↔ `KAI\ TOU\S FARMAKOU/S`
  - `XR+MY` ↔ `E)PAOIDOI\`
  - `B/LH+/YHM` ↔ `TAI=S FARMAKEI/AIS AU)TW=N`
- Deut 18:10–11:
  - `W/MK$P` ↔ `FARMAKO/S`
  - `XBR` ↔ `E)PAOIDH/N`
- Dan OG 2:2:
  - `L/XR+MYM` ↔ `TOU\S E)PAOIDOU\S`
  - `W/L/)$PYM` ↔ `KAI\ TOU\S MA/GOUS`
  - `W/L/MK$PYM` ↔ `KAI\ TOU\S FARMAKOU\S`

In generated modules these are joined by the stable `catss_alignment_id`;
the public example should demonstrate that join rather than reproduce raw CATSS
tables.

## “Passing through fire” probe

The report contrasts passages in which the same broad ritual domain receives
different Greek treatment. The raw alignment evidence confirms that this is a
good example for showing the limit between corpus evidence and interpretation:

- Deut 18:10 has `M(BYR` ↔ `PERIKAQAI/RWN`, with the child and fire
  expressions in adjacent aligned rows;
- Ezek 16:21 has `B/H(BYR` ↔ `E)N TW=| A)POTROPIA/ZESQAI/`;
- Ezek 23:37 has `H(BYRW` ↔ `DIH/GAGON` and `L/)KLH` ↔
  `DI' E)MPU/RWN`;
- Jer 32:35 maps the MT reference to LXX Jer 39:35 and uses
  `L/H(BYR` ↔ `TOU= A)NAFE/REIN`.

The corpus can show these lexical/versification differences. Calling one
rendering “magical” and another “cultic” is a scholarly interpretation and must
be labelled as such.

## Implementation decision

This ticket is documentation-only. It adds no production behavior and therefore
does not need a RED production test. The deliverable will be:

- one case-study document with executable Python snippets using standard
  Text-Fabric APIs and the two generated CATSS-TF modules;
- a compact result table from the pinned LXX parent;
- selected alignment examples expressed through the module join workflow;
- explicit scope/coverage warnings and a “where to go next” section;
- README navigation.

No CATSS, BHSA, LXX, generated module, or extracted corpus table will be committed.
