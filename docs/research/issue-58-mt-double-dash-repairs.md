# Research — issue #58 MT-column `--` rows

## Scope

The #53 complete-snapshot audit found exactly four current CATSS alignments with:

- zero MT lexical elements;
- non-empty Greek lexical material;
- first MT-column-A token `--`;
- explicit Hebrew column-B reconstruction material.

The rows are:

| source | CATSS header | original MT cell | Greek cell |
| --- | --- | --- | --- |
| `01.Genesis.par` | Gen 22:16 | `--=;M/MN/Y <22.12> <sp>` | `DI' E)ME/` |
| `01.Genesis.par` | Gen 48:13 | `-- =;)T/M <48.10>` | `AU)TOU\S` |
| `02.Exodus.par` | Exod 10:24 | `--=;)LH/YKM <10.8>` | `TW=| QEW=| U(MW=N` |
| `15.1Chron.par` | 1Chr 11:20 | `-- =B/P(M )XT` | `E)N KAIRW=| E(NI/` |

These four rows are the first current complete-corpus blocker after #50.

## Documentary evidence

Emanuel Tov's CATSS Volume 2 symbol list documents:

- Greek-column `---`: Hebrew counterpart lacking in LXX (minus in LXX);
- Hebrew-column `--+`: element “added” in Greek (plus in LXX);
- `''`: long minus/plus;
- `---{x}` / `--+{x}`: apparent minus/plus for long stretches.

The same manual describes optional Hebrew column B as reconstructed/retroverted Hebrew
material associated with the Greek. It does **not** document bare Hebrew-column
`--` as a separate alignment category.

Reference:
https://www.emanueltov.info/docs/books/books.CATSS2.pdf

Two independent open parser reconstructions reinforce the closed vocabulary:

- `codykingham/CATSS_parsers` recognizes Hebrew `--+` and `---`, but has no
  documented Hebrew `--` semantic;
- `curran-gehring/catss` recognizes Hebrew `--+` as LXX-plus and Greek
  `---` as LXX-minus, but not Hebrew `--`;
- an older CrossWire parser added bare `--` only as a guessed Greek-minus variant and
  labels that addition “probably wrong”; it gives no support for Hebrew-side `--`.

## Contextual evidence from all four current rows

Each row has the shape that CATSS normally writes as a Hebrew-side LXX-plus with a
column-B reconstruction:

- no formal MT equivalent in column A;
- non-empty Greek material;
- reconstructed Hebrew in column B;
- in three cases the reconstruction carries an explicit contextual source reference;
- the fourth has a plain reconstructed Hebrew phrase.

The source contexts also make a generic “minus” interpretation impossible: Greek is
present, and the reconstructed Hebrew explains that Greek material rather than an
omitted Greek counterpart.

## Decision R58-1 — treat the four current forms as exact source anomalies

The evidence establishes what the four rows mean, but not a general documented
semantics for every hypothetical Hebrew `--`. Therefore do **not** add `--` to the
general LXX-plus marker set.

Instead, extend the existing exact source-repair mechanism with four entries that
normalize only these source+reference+MT-cell+Greek-cell identities from `--...` to
the equivalent documented `--+...` semantic form.

## Decision R58-2 — preserve original source provenance

For each repair:

- `raw_lines`, `mt_raw`, `lxx_raw` and `catss_alignment_id` remain based on
  exact upstream text;
- semantic `mt_col_a` becomes `--+`;
- column B remains unchanged;
- `is_lxx_plus=True`;
- lexical counts remain zero MT / nonzero Greek;
- one typed `source_repair` annotation records original and corrected semantic MT
  cells.

## Decision R58-3 — fail closed on every other `--`

Any different source, reference, MT cell or Greek cell remains unmodified. If a future
snapshot introduces additional Hebrew-side `--` rows, complete-snapshot tests must
fail and require new research rather than silently generalizing this repair.


## Decision R58-4 — do not reinterpret bare `--` as apparent-minus

A competing implementation hypothesis treated `--` + column B + non-empty Greek as
a structural spelling of MT apparent-minus. The primary/current corpus evidence does
not justify that generalization.

The upstream Genesis data contain documented LXX-plus rows with the same column-B
structure, for example Gen 3:10 `--+ =;MTHLK <3.8>\tPERIPATOU=NTOS` and Gen 22:13
`--+ =:YCXQ\tISAAK`. Thus the presence of a reconstructed column B is compatible
with an ordinary LXX-plus event and is not evidence for apparent-minus by itself.

The four anomalous rows are each exactly one missing `+` away from that documented
surface grammar. Gen 22:16 is especially diagnostic: its column-B form
`;M/MN/Y <22.12>` points back to the explicit MT phrase `M/MN/Y` aligned with
`DI' E)ME/` in Gen 22:12. Treating the row as an exact lost-`+` source anomaly is
therefore narrower than assigning a new generic meaning to undocumented bare `--`.

The exact-repair table remains deliberately closed. A future bare-`--` row does not
inherit LXX-plus semantics without separate evidence.
