# Research — issue #68 doubt-decorated Greek `---?`

## Scope

Issue #64 found exactly seven current alignments with lexical MT material, zero Greek
lexical tokens, and Greek-side first token `---?`:

- JudgA 20:6;
- 1 Chr 12:38;
- 1 Chr 29:9;
- Ps 35:20 (`---? [34.20]`);
- Isa 51:3 (two rows);
- Jer 25:4.

The parser already emits a generic `doubt` annotation from the question mark, but
`is_lxx_minus` remains false because marker recognition currently requires exact
first-token membership in `{"---", "--", "----"}`.

## Documentary/prior-parser evidence

Cody Kingham's reconstruction of CATSS notation treats doubt compositionally:

- a suffix `?+` following a non-space item “indicates doubt on the word or
  interpretation of the translation strategy”;
- `---` is independently recognized as an alignment/minus siglum.

The regex ordering explicitly permits the doubt marker to tag another CATSS construct;
it is not presented as a different alignment category.

CATSS-TF likewise already models `?` independently as a typed `doubt` annotation.
Therefore the faithful representation is one LXX-minus fact plus one doubt fact, while
preserving raw spelling `---?`.

## Decision R68-1 — recognize only the documented decorated marker

Greek first token `---?` is compositionally equivalent to:

- underlying Greek-side `---` LXX-minus;
- independent doubt annotation `?`.

Do not strip arbitrary punctuation from marker tokens and do not infer minus from Greek
lexical emptiness.

## Decision R68-2 — preserve raw evidence

`lxx_raw`, physical `raw_lines`, source lines and `catss_alignment_id` remain
unchanged. No `source_repair` annotation is appropriate because the source spelling
is meaningful, not corrupt.

## Decision R68-3 — complete population is closed

The current 46-file snapshot contains exactly seven `---?` residuals. A permanent
guard should require all seven to be LXX-minus+doubt and require no remaining
MT-nonempty/Greek-empty first-token `---?` residual.
