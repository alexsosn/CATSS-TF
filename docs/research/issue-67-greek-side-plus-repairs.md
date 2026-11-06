# Research — issue #67 Greek-side `--+` source anomalies

## Trigger

The complete 46-file Greek-empty audit in #64 found exactly six alignments with lexical
MT material, zero Greek lexical tokens, and Greek-side raw text beginning with `--+`:

| source | reference | MT raw | Greek raw |
|---|---|---|---|
| `01.Genesis.par` | Gen 34:29 | `KL` | `--+` |
| `18.Esther.par` | Esth 7:4 | `W/)LW` | `--+` |
| `23.Prov.par` | Prov 11:31 | `)P KY` | `--+` |
| `23.Prov.par` | Prov 24:5 | `GBR` | `--+` |
| `23.Prov.par` | Prov 30:32 | `L/PH` | `--+ {x}` |
| `41.Jer.par` | Jer 51:57 | `PXWT/YH` | `--+ [28.57]` |

These six are the current first blocker for standalone canonical materialization.

## Documentary and prior-parser evidence

The CATSS convention reconstructed in the open parser literature is side-specific:

- Hebrew-column `--+`: element added in the Greek (LXX-plus);
- Greek-column `---`: no Greek counterpart (LXX-minus).

The current independent parser at `curran-gehring/catss` encodes the same directional
distinction: `--+` is detected only from the Hebrew column, while Greek `---` marks
LXX-minus.

Cody Kingham's CATSS repair pipeline contains many explicit source corrections and
normalizations, but it does not define Greek-side `--+` as a legitimate semantic
category. Its bulk normalization also distinguishes `---` and `--+` rather than
assigning them side-independent meaning.

## Complete-snapshot evidence

All six Greek-side `--+` rows are omission-shaped:

- MT lexical count is positive;
- Greek lexical count is zero after markup removal;
- surrounding rows contain normal MT↔Greek alignments;
- no transposition evidence is present.

Examples:

- Gen 34:29: `KL -> --+` occurs between `W/)T -> KAI\` and
  `)$R -> O(/SA`;
- Jer 51:57: `PXWT/YH -> --+ [28.57]` sits between ordinary Greek alignments
  carrying the same contextual reference.

The two decorated forms are also compatible with an underlying minus marker:

- Prov 30:32 carries independent `{x}` apparent-plus/minus annotation;
- Jer 51:57 carries independent contextual reference `[28.57]`.

Neither decorator supplies Greek lexical material.

## Decision R67-1 — exact source repair, not new generic syntax

There is no evidence that Greek-side `--+` should become a general parser synonym for
LXX-minus. The narrow fail-closed interpretation is that these six current rows contain
a source/export marker anomaly where the documented Greek-side `---` was represented
as `--+`.

Repair only exact identities consisting of:

- source filename;
- chapter and verse;
- exact MT raw cell;
- exact Greek raw cell.

A lookalike at another reference or with different cells must remain untouched.

## Decision R67-2 — semantic Greek cell becomes `---`

For the six exact identities, use these semantic Greek cells:

- `--+` → `---`;
- `--+ {x}` → `--- {x}`;
- `--+ [28.57]` → `--- [28.57]`.

This makes `is_lxx_minus=True`, keeps Greek lexical count zero, and lets the existing
technique-v1 model derive `omission_vs_mt=True`.

The decorators remain independently queryable.

## Decision R67-3 — raw provenance and identity do not change

The parser must preserve:

- original physical `raw_lines`;
- original `mt_raw` and `lxx_raw` (including raw `--+`);
- source-derived `catss_alignment_id`.

The repair must be explicit as one typed `source_repair` annotation on side `lxx`,
with raw source cell and corrected semantic cell in its payload.

## Decision R67-4 — generalize repair plumbing, not repair semantics

Existing source repairs are MT-side only. Supporting a Greek-side repair should make the
internal repair record side-aware so provenance can be represented faithfully, but must
not broaden the closed identity tables or infer repairs from cardinality.
