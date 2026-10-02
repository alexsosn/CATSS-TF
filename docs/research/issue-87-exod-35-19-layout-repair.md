# Research — issue #87 Exod 35:19 source-layout corruption

## Ground truth

The raw upstream `02.Exodus.par` sequence is:

```
16273 Exod 35:19
...
16283 ^ ^^^ =L/$RT {...?H/&RD} #    {+} E)N AI(=S LEITOURGH/SOUSIN
16284
16285 Exod 1:10
16286     #
16287
16288 Exod 35:19
16289 --+    E)N AU)TAI=S
16290 W/)T BGDY    KAI\ TOU\S XITW=NAS
...
```

The embedded `Exod 1:10` cannot be a real header: it occurs inside the continued
35:19 row and is immediately followed by another 35:19 header.

This is independently documented in
`codykingham/CATSS_parsers@dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35`
`patch_catss.py`. Its comment explicitly identifies the blank lines and
`Exod 1:10` as corruption, removes them, retains the orphan continuation line
`\t#`, and removes the now-redundant second `Exod 35:19` header.

The effective semantic stream is therefore the original physical lines 16283, 16286,
16289, ... under the single original Exod 35:19 header.

## Why the current parser fails

`parse_parallel_text()` recognizes headers before parsing rows. When line 16285 is seen,
it flushes the pending 35:19 continuation, so the trailing `#` on line 16283 becomes a
`malformed_continuation`. The orphan `\t#` is then parsed under false Exod 1:10 and
produces the second malformed-continuation diagnostic. Line 16288 starts a new 35:19
record.

A generic rule such as “ignore headers while a continuation is pending” is unsafe:
real headers are structural evidence and malformed rows elsewhere must remain visible.

## Decision R87-1 — exact pre-header layout repair

Normalize this corruption before verse/header recognition, but only for
`02.Exodus.par` and only when the complete contiguous raw signature matches the known
sequence.

The semantic line stream must:

- retain original line 16283 unchanged;
- suppress the corrupt blank/header wrapper lines 16284, 16285, 16287 and 16288 from
  semantic header parsing;
- retain original continuation line 16286 unchanged and with its original physical line
  number;
- retain line 16289 and all following data unchanged.

Do not renumber surviving source lines.

The matcher should use the exact raw content sequence, not only historical numeric line
positions, so an upstream insertion elsewhere cannot make the repair hit unrelated data.

## Decision R87-2 — explicit document-level provenance

Pre-parser repair must not make suppressed bytes disappear from the IR.

Add an immutable source-layout-repair provenance record to `ParallelDocument` containing:

- repair kind / stable name;
- original physical line numbers;
- original raw line strings, including blank lines and both corrupt headers;
- surviving semantic line numbers;
- a concise rationale.

The normal alignment keeps its actual data-row `source_lines` and `raw_lines`; therefore
alignment identity continues to be derived from original physical evidence rather than
from renumbered or invented rows.

Canonical-corpus work should eventually materialize these repair provenance records as
first-class provenance nodes. Projection modules may expose a scalar repair provenance
feature only where it can be attached faithfully; no JSON blob is required.

## Decision R87-3 — no fabricated Exod 1:10 verse

After repair, parsing the focused source window must yield exactly one Exod 35:19 verse
record for the affected sequence and no Exod 1:10 record created from the corrupt
embedded header.

The real Exod 1:10 earlier in the file remains unaffected.

## Decision R87-4 — closed failure behavior

If any member of the exact corruption signature changes, CATSS-TF must not partially
apply this repair. The ordinary parser should then surface the raw problem through its
existing diagnostics.

No generic continuation/header heuristic is introduced.

## Regression scope

The complete 46-file snapshot gate must prove:

- the exact corruption signature occurs once;
- one layout repair provenance record is emitted;
- both current Exod 35:19 `malformed_continuation` diagnostics disappear;
- no false Exod 1:10 record is created at the corrupt location;
- surviving original line numbers are preserved;
- all original lines in the repair window are recoverable from provenance;
- unrelated parser diagnostic counts do not silently change.
