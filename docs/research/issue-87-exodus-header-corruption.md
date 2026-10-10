# Research — #87 Exodus 35:19 interposed source corruption

## Evidence

The current upstream `02.Exodus.par` has a continued data row at Exod 35:19,
then a blank physical line, an impossible `Exod 1:10` header, a lone `#`
continuation marker, another blank, a duplicate `Exod 35:19` header and a
second data fragment `--+ / E)N AU)TAI=S`.

Independent prior implementation:
`codykingham/CATSS_parsers/patch_catss.py`, function
`patch_parallel`, comments on physical source lines 16283–16289 and
explicitly drops the false header, blanks and duplicate header while retaining
the lone `#` row. Source:
https://github.com/codykingham/CATSS_parsers/blob/master/patch_catss.py

The current CATSS-TF `parse_parallel_text` treats a blank as ignorable,
any syntactically valid `Exod 1:10` as a hard verse boundary, and the lone
`#` as a continuation without a preceding row. It therefore reports two
`malformed_continuation` diagnostics and creates a spurious verse.

## Design decision

Recognize **only** the exact seven-physical-line pattern under
`02.Exodus.par` and current `Exod 35:19`, with both lexical fragment
cells checked. Treat the five interposed physical lines as source-layout
evidence on the same alignment; preserve their exact source line numbers and
raw contents alongside the actual first/last fragment in
`AlignmentRecord.source_lines/raw_lines`. The two blanks and both header
strings must be preserved, not discarded or lexically interpreted.

Use normal MT/LXX physical-row parsing for the two real data fragments.
The intervening lines become `layout_dummy` rows, without semantic tokens.
The lone `#` remains raw provenance; the first fragment's trailing
`#` already signals continuation. The final fragment must join this pending
record without extending generic cross-header continuation rules.

The repair's source identity uses the source basename, exact neighboring
raw cell identities and seven-line ordering, **not** absolute line numbers;
adding unrelated earlier source lines must not disable the repair. A
lookalike in a different book/verse or with changed cells is unrepaired.

The existing deterministic alignment hash already incorporates all
`source_lines/raw_lines`; no hash exception or source rewrite is needed.

## Risks to test

- No hidden `Exod 1:10` verse under exact input.
- Every one of seven original physical lines, including blanks, remains
  traceable to exactly one logical alignment and counted in provenance.
- No transposition/plus-minus evidence is fabricated.
- New normal parser behavior remains unchanged on nearly identical input.
- The complete 46-file audit locates one exact match, confirms zero
  `malformed_continuation` for this source neighborhood, and checks
  total physical line accounting; any upstream drift fails the gate.
