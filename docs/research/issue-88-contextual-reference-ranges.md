# Research — issue #88 CATSS contextual-reference ranges

## Trigger

The complete CATSS snapshot has one remaining `invalid_lxx_reference` diagnostic whose
syntax is structurally meaningful rather than corrupt:

- source: `06.JoshB.par`;
- source record: second `JoshB 9:2` header;
- raw row: `{...} <8.30-35>\t[[9.2a-2f]]`;
- MT lexical count: 0;
- Greek lexical count: 0;
- MT carries the existing remote-transposition placeholder `{...}`;
- MT also preserves the contextual note `<8.30-35>`;
- Greek carries the double-bracket contextual reference range `[[9.2a-2f]]`.

This must not be repaired into lexical material.

## Grounding in the source snapshot

The immediately preceding CATSS records prove the meaning of the compact Greek range.
The source maps six consecutive MT verses into six LXX subverses:

- JoshB 8:30 → `[9.2a]`;
- JoshB 8:31 → `[9.2b]`;
- JoshB 8:32 → `[9.2c]`;
- JoshB 8:33 → `[9.2d]`;
- JoshB 8:34 → `[9.2e]`;
- JoshB 8:35 → `[9.2f]`.

After the ordinary lexical `JoshB 9:2` record, CATSS emits a second structural record:

```
JoshB 9:2
{...} <8.30-35>    [[9.2a-2f]]
```

Thus `[[9.2a-2f]]` denotes the inclusive LXX span 9:2a through 9:2f and corresponds
to the already explicit six-way relocation of MT 8:30–35.

The double brackets are already recognized by the parser as a contextual-reference
annotation family. The problem is specifically that the structured Greek-reference
parser only accepts a scalar verse/subverse.

## Current parser limitation

`GreekReference` currently represents one scalar target:

- optional chapter;
- verse;
- optional subverse;
- raw spelling.

`_GREEK_REFERENCE_VALUE` accepts scalar `chapter:verse+subverse` or
`verse+subverse`. `_extract_greek_references()` therefore cannot turn
`9.2a-2f` into structured data and emits `invalid_lxx_reference`.

Treating the two endpoints as two ordinary `GreekReference` values is not correct.
The resolver deliberately rejects multiple distinct scalar references on one alignment
as `multiple_lxx_references`; a range has different semantics from two alternative
or competing targets.

## Parent-model grounding

The configured CenterBLC LXX parent contains first-class `subverse` structure.
CATSS-TF's `TextFabricLxxProvider.get_span()` already accepts
`(book, chapter, verse, subverse)` and resolves a subverse to its unique parent
`subverse` node plus the words below it.

Therefore no synthetic LXX nodes are needed. The range can be expanded deterministically
to the six existing parent subverse spans 9:2a … 9:2f. The implementation gate must
verify these six endpoints against the exact pinned CenterBLC/LXX release before merge.

## Projection consequences

This row is structural, not lexical.

### LXX projection

The current LXX resolver treats Greek-empty remote-transposition rows as one structural
anchor at one scalar reference. A range needs six ordered structural memberships/anchors,
one for each parent subverse a–f, all retaining the same `catss_alignment_id`.

The generic scalar-reference resolver must remain unchanged for ordinary rows.
Range expansion should occur only for a typed range.

The current shared TF compiler rejects duplicate anchors for the same
`(source, alignment_id)`, so a range cannot be forced through the existing
single-anchor contract. It needs a dedicated range-membership event/feature contract
or an explicitly range-aware anchor identity that includes member ordinal/node.

### BHSA projection

The second `JoshB 9:2` record contains no MT lexical positions. Today, after validation,
the ordinary BHSA verse resolver would compare zero positions against the lexical BHSA
9:2 parent and report a word-count mismatch.

A typed contextual-range record must therefore be excluded from ordinary lexical
verse-position matching. Its raw MT contextual note `<8.30-35>` remains preserved.
Structuring that MT source range as BHSA parent memberships is useful, but it is a
separate semantic step from parsing the LXX range and must not be guessed from a generic
angle-bracket note without a documented grammar.

For #88 the minimum safe BHSA behavior is: recognize the alignment as a structural
range carrier and do not let it corrupt lexical verse alignment.

## Canonical corpus consequence

The open canonical-corpus work (#40 / PR #47) already models scalar Greek references as
first-class `reference` child nodes. A range cannot be losslessly represented by
silently materializing only its first or last scalar endpoint.

Once #88's parser contract is fixed, PR #47 should consume it as a first-class
`reference_range` child node (or an equivalent explicit node contract) with query-native
start/end chapter, verse and subverse features plus raw spelling. The canonical corpus
is the appropriate place for a first-class relation object because a TF module may add
features to parent nodes but cannot add new nodes.

This dependency should be integrated into #47 before that PR is finalized; #88 does not
need to duplicate the entire canonical materializer on its own branch.

## Data model decision R88-1 — first-class GreekReferenceRange

Add a separate immutable `GreekReferenceRange` value rather than overloading
`GreekReference`.

Required fields:

- start chapter (optional in the same sense as scalar references);
- start verse;
- start subverse;
- end chapter (optional / inherited when omitted in source);
- end verse;
- end subverse;
- raw source spelling.

`AlignmentRecord` receives `lxx_reference_ranges` separately from
`lxx_references`.

This keeps the existing scalar API stable and makes accidental first-endpoint collapse
impossible.

## Grammar decision R88-2 — closed, evidence-based range syntax

Implement the observed contextual range family needed by the snapshot, including
`9.2a-2f` where:

- `9` is chapter;
- start endpoint is verse 2, subverse a;
- the right endpoint inherits chapter 9 and spells verse 2, subverse f.

Do not add speculative open-ended ranges, lists, reversed ranges, implicit alphabetic
expansion across verses, or arbitrary punctuation.

Reject malformed/reversed ranges with an explicit diagnostic rather than guessing.

## Resolution decision R88-3 — inclusive ordered subverse expansion

A valid same-verse alphabetic range such as 9:2a–9:2f expands in order to
a,b,c,d,e,f.

Each member must resolve through the ordinary pinned-parent provider. Missing members,
ambiguous structure, or unsupported cross-verse semantics fail closed.

The projection preserves:

- one source `alignment_id`;
- range raw spelling;
- member ordinal;
- total member count;
- start/end endpoint metadata;
- parent subverse node identity.

No lexical token or fabricated parent node is created.

## Preservation decision R88-4 — keep both raw contextual carriers

The parser must continue to preserve:

- raw line `{...} <8.30-35>\t[[9.2a-2f]]`;
- MT annotation `{...}`;
- MT note `<8.30-35>` and its payload;
- Greek contextual-reference annotation with raw `[[9.2a-2f]]` and payload
  `9.2a-2f`;
- stable source-derived alignment id.

The new structured range is additional typed semantics, not a textual rewrite.

## Scope boundary

#88 should implement and test:

1. range parsing and validation;
2. structural LXX range resolution against the exact parent;
3. query-native LXX module representation on the existing six subverse nodes;
4. BHSA lexical-resolver exclusion for this structural carrier;
5. complete-snapshot regression proving the last invalid Greek-reference diagnostic is
   removed without broadening unrelated syntax;
6. handoff/integration note for canonical PR #47.

It should not infer arbitrary MT angle-note ranges, invent lexical correspondences, or
weaken scalar-reference ambiguity checks.
