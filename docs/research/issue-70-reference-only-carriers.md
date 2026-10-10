# Research — issue #70 Greek contextual-reference-only carriers

## Trigger

Issue #64 isolated the last two known MT-nonempty / Greek-empty residual alignments
whose Greek cell contains no lexical token and consists only of a contextual square-
bracket reference:

- 1/3 Kgs 22:50: `)X)B -> [16.28g]`;
- 1 Esdr 6:4: `L/KM -> [e5.3]`.

Both are already preserved as typed Greek-side `contextual_reference` annotations.
Technique-v1 currently rejects them because lexical Greek cardinality is zero and they
carry neither LXX-minus nor transposition flags.

## Documentary/prior-parser evidence

CATSS square-bracket material is reference markup, not lexical Greek. The prior CATSS
parser distinguishes normal Greek versification references from contextual/cross-
reference notation, and the historical data format uses such references to point to
material aligned elsewhere.

This makes a reference-only cell materially different from an omission marker:
the source supplies an explicit pointer to another textual location rather than saying
that the Hebrew element lacks a Greek rendering.

## Research questions

1. What is the complete current Greek-side `contextual_reference` population?
2. How many rows contain no standalone Greek lexical token?
3. Are the two residual rows structurally tied to neighboring rows bearing the same
   contextual reference and real LXX-minus or lexical Greek material?
4. Are there other reference-only shapes that would make a generic carrier rule unsafe?
5. Should technique-v1 admit a reference-only carrier as neutral
   (neither addition nor omission), or should it be modeled as a transposition class?
6. Can the rule be expressed entirely from typed reference evidence plus lexical
   cardinality, without parsing raw bracket syntax in technique code?

## Snapshot research gate

Enumerate every Greek-side `contextual_reference` annotation in the current 46-file
snapshot, recording source/reference, raw cells, cardinality, typed annotations,
transposition/minus flags, and immediate neighboring alignments. Summarize the
reference-only subset separately.

No production behavior changes during this research gate.


## Complete-snapshot result

The current 46-file snapshot contains **40,397** alignments with a typed Greek-side
`contextual_reference` annotation. Of these, **2,819** have lexical MT material and
zero standalone Greek lexical tokens.

That zero-Greek population is already almost entirely explained by stronger typed
semantics:

- 2,653 rows are LXX-minus;
- 165 rows carry transposition evidence;
- exactly **two** rows have neither LXX-minus nor transposition evidence.

Those two residual identities are exactly:

1. `13.1Kings.par`, 1/3Kgs 22:50, `)X)B -> [16.28g]`;
2. `17.1Esdras.par`, 1Esdr 6:4, `L/KM -> [e5.3]`.

This rules out a generic “contextual reference admits Greek-empty cardinality” rule.

## Target 1 — 1/3 Kgs 22:50 is a missing minus marker

The current CATSS neighborhood is:

- `)MR -> EI)=PEN [16.28g]`;
- `)XZYHW -> --- [16.28g]`;
- `BN -> --- [16.28g]`;
- `)X)B -> [16.28g]`;
- `--+ =MLK -> O( BASILEU\\S [16.28g]`;
- `--+ =:Y&R)L -> ISRAHL [16.28g]`.

The underlying Greek 3 Kgdms 16:28g names only “the king of Israel”; it does not
contain Ahaziah, “son”, or Ahab in this clause. The source evidence therefore supports
three consecutive MT elements absent from Greek. CATSS marks the first two with
`---` but leaves the Ahab row with only the contextual reference.

Decision: exact source/alignment repair to semantic `--- [16.28g]`, preserving raw
`[16.28g]`. Implementation is split to #81.

Primary CATSS source:
<https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/13.1Kings.par>

Greek 3 Kgdms 16:28g:
<https://theologianspress.org/bible/3kingdoms/16>

## Target 2 — 1 Esdr 6:4 is missing a real Greek token

The CATSS neighborhood is:

- `&M {...+(M} -> SUNTA/CANTOS [e5.3]`;
- `L/KM -> [e5.3]`;
- `+(M -> {...} [e5.3]`.

The Greek text of 1 Esdras 6:4 explicitly contains `ὑμῖν` in
`τίνος ὑμῖν συντάξαντος ...`. CATSS Beta Code elsewhere uses `U(MI=N` for this
form and the prior parser documentation directly demonstrates `L/KM -> U(MI=N`.

Decision: this row is not an omission and is not a neutral zero-token carrier. Its
Greek lexical counterpart is missing from the alignment cell. Candidate exact semantic
repair: `U(MI=N [e5.3]`, subject to parent-token verification before implementation.
Implementation research is split to #82.

Greek 1 Esdras 6:4:
<https://www.die-bibel.de/en/bible/LXX/1ES.6>

Prior CATSS parser documentation:
<https://github.com/codykingham/CATSS_parsers/blob/dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35/parallel_readme.md>

## Decision R70-1 — no contextual-reference carrier exception

Technique-v1 remains fail-closed when contextual reference is the only evidence. The
two residual rows have different source defects and require different exact repairs.
No production semantics change in #70 itself.

## Follow-up

- #81 — exact missing `---` repair at 1/3 Kgs 22:50;
- #82 — parent-grounded restoration of missing `U(MI=N` at 1 Esdr 6:4.
