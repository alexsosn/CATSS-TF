# Research — issue #86 marker-only CATSS alignment at 1 Esdras 4:28

## Exact source evidence

The complete-snapshot audit for #54 identified one 1 Esdras 4:28 row:

```
--- ''    --+
```

Source: `17.1Esdras.par`; physical line 2173 on the audited snapshot;
alignment ID `catss:17.1Esdras.par:7e452856253057a69b02`.

Both lexical sides are empty. The Greek-side text is the marker `--+` alone; the
MT side carries a leading `---` followed by the column marker `''`.
The immediately preceding four lines are `--+ ''` on the MT side and lexical
Greek additions `AI( XW=RAI`, `EU)LABOU=NTAI`, `A(/YASQAI`, `AU)TOU=`.
The next record starts the new header `1Esdr 4:29`.

## Distinctness

This row is not among the 61 ordinary MT-side apparent-minus alignments because
it has zero Greek lexical material. It is also structurally different from
Jonah 4:3, where a lexical MT token is paired with two Greek words.

The prior `codykingham/CATSS_parsers` regex treats `---` as a separate
apparent-MT-minus siglum (optionally decorated by `''`) and `--+` as the
Hebrew-column LXX-plus siglum. Neither establishes a generic Greek-column
meaning for `--+`.

The reconstructed CATSS guide describes `''` as a column modifier, but the
currently checked open-source evidence does not establish whether the isolated
end-of-verse double marker represents a ditto/column carry-over, a source
corruption, or a deliberate empty structural transition.

## Decision R86-1 — retain fail-closed status

Do **not** interpret this zero/zero row as a normal LXX-plus, apparent-minus,
or omission from marker spelling. Do not suppress the contradictory cardinality
gate solely because this single row exists.

The raw row, source line and stable alignment ID must remain recoverable.
The standalone canonical corpus may preserve a source-level structural record,
but should not fabricate lexical tokens or assign translation technique to it
without documentary evidence.

## Next research gate

Compare the full page on column modifiers and apparent MT-minus in the original
1986 Tov CATSS manual and the 1991 CCAT `00.ReadReParallel.txt`; also inspect
the corresponding physical source text and any previous export/patch behavior.

If those sources establish a definite marker-only state, write a narrow plan with
a RED test for this exact source identity, plus negative tests for other zero/zero
apparent-minus markers. Otherwise document this as an unresolved source semantic
without weakening shared technique-v1 rules.
