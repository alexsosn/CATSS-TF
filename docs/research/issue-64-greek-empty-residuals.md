# Research — issue #64 residual Greek-empty alignments

## Trigger

Canonical corpus materialization on #47 now reaches a new fail-closed boundary after
#57 and #58: an alignment in `01.Genesis.par` with lexical MT material, no Greek
lexical tokens, and raw Greek `--+`.

Technique-v1 correctly refuses to infer omission semantics from cardinality alone.
The marker spelling is especially unsafe here because `--+` is documented as a
Hebrew-column LXX-plus marker; a Greek-column occurrence cannot inherit that meaning
without evidence.

## Research questions

1. How many current alignments have `mt_count > 0`, `lxx_count == 0`, are not
   already `is_lxx_minus`, and carry no transposition evidence?
2. What raw Greek-side forms account for them?
3. Are they isolated source anomalies, systematic legacy spellings, continuation
   artifacts, or another documented category?
4. Do the classes differ enough to require separate implementation tickets?

## Gate

A temporary complete-snapshot audit enumerates every residual row with:

- source and verse header;
- physical source lines;
- raw MT and Greek cells;
- first Greek-side token;
- MT/LXX counts;
- typed annotations and transposition flags;
- immediately neighboring alignment raw cells within the same verse.

No production semantics are changed during this research phase. The audit must remain
descriptive; any behavior change follows a separate plan and RED-first implementation.


## Complete-snapshot result

The current 46-file snapshot contains **298** MT-nonempty / Greek-empty residual
alignments after excluding already typed LXX-minus and transposition cases.

Surface classes:

| Greek-side first token | count |
| --- | ---: |
| physically empty | 280 |
| `---?` | 7 |
| `--+` | 6 |
| `{p}` | 3 |
| contextual reference only | 2 |

The 280 physically empty cases are not 280 independent omission events.
The parser reports 206 residual alignments from physically unsplit data lines and 74
formally split rows with an empty Greek cell. Representative pairs in both Daniel
traditions are a normal Hebrew-side `DNY)L` row with an empty Greek cell immediately
followed by an unsplit `DANIHL` line. Similar fragments are visible around book-name
strings in Isaiah, Deuteronomy, Chronicles, Ezekiel, Nehemiah and elsewhere.

## Prior-parser evidence for export-orphan corruption

Cody Kingham's open CATSS repair pipeline independently diagnoses the same physical
corruption. Its `patch_catss.py` states that lines without a tab are orphaned from
their original line because a bad export/book-reference regex inserted newlines inside
text whenever book-name-like character sequences occurred.

That implementation repairs:

- non-Psalms orphan lines by appending the physical fragment back to the **Greek**
  column of the preceding line;
- Psalms orphan lines by prepending the fragment to the **Hebrew** column of the
  following line, because `PS` occurs inside Hebrew transcription;
- a special double-orphan Psalms case before applying the same general rule.

This directly explains why one physical corruption produces both an unsplit residual
and a neighboring split row whose Greek side is empty.

Reference implementation:
`codykingham/CATSS_parsers@dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35:patch_catss.py`.

## Semantic residual classes after layout repair

The remaining 18 split rows are heterogeneous and must not share a generic
Greek-empty exception:

1. **6 Greek-side `--+` rows.** `--+` is documented as a Hebrew-column LXX-plus
   marker, not a Greek-column marker. All six current Greek-side occurrences have
   MT lexical material and no Greek lexical material. Representative contexts
   (Gen 34:29; Esth 7:4; Prov 11:31; Prov 24:5; Prov 30:32; Jer 51:57) read as
   omissions from Greek; Gen 34:29 for example aligns `KL` against `--+` between
   `W/)T -> KAI\` and `)$R -> O(/SA`. Treat as a separate source-anomaly class
   pending an exact-repair implementation.
2. **7 `---?` rows.** These are compositionally a documented Greek-side `---`
   LXX-minus decorated by the general CATSS doubt marker `?`. The current parser
   extracts `doubt` but fails to retain the underlying LXX-minus flag.
3. **3 Greek-preverb rows.** Two are `{p} ---`; one (Sir 23:17) is bare `{p}`.
   `{p}` is already typed as `greek_preverb`; bare preverb evidence must not be
   mislabeled as omission merely because it has zero standalone Greek tokens.
4. **2 contextual-reference-only rows.** Their Greek cell consists solely of a
   cross-reference (`[16.28g]`, `[e5.3]`). They are reference carriers and need
   separate research from omissions.

## Split decision

Issue #64 is therefore a classification/research umbrella. Implementation should be
split by cause:

- export-orphan physical-line repair;
- six Greek-side `--+` source anomalies;
- compositional `---?` LXX-minus recognition;
- zero-token Greek-preverb carriers;
- contextual-reference-only carriers.

Technique-v1 remains fail-closed for every class until its evidence is modeled.
