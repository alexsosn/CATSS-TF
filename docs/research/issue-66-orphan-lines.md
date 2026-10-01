# Research — issue #66 CATSS export-orphan physical lines

## Evidence

Issue #64 found 298 MT-nonempty/Greek-empty residual alignments. Of these, 280
have physically empty Greek text. They consist of 206 unsplit physical rows plus 74
neighboring split rows whose Greek side becomes empty because the missing fragment was
exported onto its own line.

An independent open CATSS repair pipeline
(`codykingham/CATSS_parsers@dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35`,
`patch_catss.py`) diagnoses the same source corruption: a bad export/book-reference
regex inserted line breaks when book-name-like strings occurred inside text.

Its directional repair is source-sensitive:

- outside Psalms, a no-tab orphan fragment belongs back at the end of the preceding
  **Greek** column;
- in Psalms, `PS`-triggered fragments belong at the beginning of the following
  **Hebrew** column;
- consecutive Psalms fragments must be rejoined before semantic parsing.

This explains examples such as Daniel `DNY)L` followed by orphan Greek `DANIHL`,
and the Psalms fragments whose Hebrew transcription contains `PS`.

## Required invariants

A CATSS-TF repair must preserve physical provenance rather than rewriting the source:

- every original physical line remains represented exactly once in `source_lines`
  and `raw_lines`;
- repaired logical `mt_raw` / `lxx_raw` reflect the reconstructed column content;
- alignment IDs remain deterministically derived from the complete original physical
  line sequence;
- no translation-technique fact is inferred from the corruption itself;
- an orphan that cannot be attached within the same verse remains fail-closed and
  diagnosed.

## Snapshot research gate

Before implementation, enumerate every current `column_split=False` alignment and
verify:

1. whether it has a preceding/following alignment in the same verse;
2. the source/book distribution;
3. whether any unsplit row occurs at a verse boundary where the directional repair
   would be ambiguous;
4. whether all issue-64 physically-empty residuals are explainable by this corruption.

No production behavior changes during this gate.


## Complete-snapshot result

The current 46-file snapshot contains **208** logical alignments with at least one
physical row that could not be split into CATSS columns by the current parser.

Distribution:

- Daniel OG: 82
- Daniel Theodotion: 74
- Isaiah: 25
- Psalms: 10
- Joshua B: 4
- 1 Chronicles: 3
- Esther: 2
- Nehemiah: 2
- Ezekiel: 2
- Numbers, Deuteronomy, Sirach, Lamentations: 1 each.

Adjacency audit:

- 199 have both a preceding and following alignment in the same verse;
- 8 have a preceding alignment but are last in the verse;
- 1 has no preceding alignment but does have a following alignment.

Applying the direction rule independently attested in the prior repair pipeline gives
**zero ambiguous current boundary cases**:

- every non-Psalms unsplit alignment has a preceding alignment in the same verse;
- every Psalms unsplit alignment has a following alignment in the same verse.

The 208 total includes two cases outside issue #64's MT-nonempty/Greek-empty residual
predicate; therefore the layout inventory is intentionally slightly larger than the
206 unsplit members of that semantic residual set.

Representative corruption shapes confirm that reconstruction must preserve exact
concatenation rather than inserting token separators blindly:

- Num 20:17: orphan Greek fragment `NUMA`;
- Deut 17:18: `DEUTERONO/MION`;
- 1 Chr 4:23: `AU)TOU=`;
- Esther 8:4: `ESTHKE/NAI`;
- Neh 3:1: `NEHL`;
- Psalms includes fragments as short as `)` and the consecutive Ps 68:31 fragments
  `MTR` + `PS =?M/TR`;
- Joshua contains whole no-tab corrupted rows where Hebrew and Greek material were
  cleft around an export boundary.

## Representation decision

Repair layout **before semantic interpretation**, but preserve physical provenance.

For non-Psalms, one or more unsplit physical fragments are concatenated exactly to the
raw Greek column of the immediately preceding logical row. For Psalms, consecutive
unsplit fragments are concatenated exactly to the raw Hebrew column of the immediately
following logical row.

No separator is invented: the reconstruction follows the same raw concatenation used
by the independent prior repair. The original physical line numbers and raw strings
remain attached to the reconstructed logical alignment in source order, and its
alignment id is derived from that full original physical sequence.

After successful repair, the logical row is considered column-split for downstream
validation; `unsplit_row` is reserved for an orphan that cannot satisfy the
directional rule inside one verse. No translation-technique semantic is introduced by
the repair itself.


## Physical no-tab cross-check

A second snapshot audit checked the original physical strings rather than the parser's
`column_split` flag:

- physical data lines without a tab: **208**;
- all 208 occur in alignments currently reported as `column_split=False`;
- zero no-tab physical lines are hidden inside an alignment currently considered split.

Thus the 208-alignment inventory is exactly the current physical no-tab inventory.

Four of the 208 are the Joshua B rows that the independent repair pipeline handles
with explicit manual column restorations before its generic orphan pass:

- JoshB 3:10, current source line 984;
- JoshB 4:11, line 1367 (followed by an explicit continuation fragment);
- JoshB 9:4, line 3738;
- JoshB 21:42, line 9518.

These rows contain both Hebrew and Greek material on one physical line and must **not**
be appended wholesale to the preceding Greek cell. CATSS-TF should use exact
source+verse+raw layout repairs for these four identities, preserving the original raw
line while supplying the restored MT/LXX column split.

The remaining no-tab population follows the direction-sensitive orphan rule. This
keeps the generic repair narrower than the historical pipeline while retaining its
empirically supported behavior on the current snapshot.
