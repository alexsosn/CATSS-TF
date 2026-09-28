# Research — issue #58 MT-column `--` + column-B reconstruction

## Scope

The complete #53 residual audit found exactly four current CATSS alignments whose
MT column A begins with bare `--`, has no MT lexical element, has non-empty Greek,
and also carries a Hebrew column-B reconstruction:

- Gen 22:16: `--=;M/MN/Y <22.12> <sp>\tDI' E)ME/`
- Gen 48:13: `-- =;)T/M <48.10>\tAU)TOU\\S`
- Exod 10:24: `--=;)LH/YKM <10.8>\tTW=| QEW=| U(MW=N`
- 1 Chr 11:20: `-- =B/P(M )XT\tE)N KAIRW=| E(NI/`

These currently fail technique-v1 because they are Hebrew-empty/Greek-nonempty but
are neither `--+` LXX-plus nor typed `---` apparent-MT-minus.

## Documentary/prior-parser evidence so far

CATSS documentation describes Hebrew column A as the formal MT-equivalent column and
column B as selected retroverted Hebrew readings presumed behind the Greek when the
Greek appears to reflect a reading different from MT.

Cody Kingham's open parser reconstruction documents:

- `--+` in Hebrew column A as an element added in Greek;
- `---` in Hebrew column A as an apparent minus in MT over against Greek;
- `=...` as introducing Hebrew column B;
- `=;...` as a contextual retroversion in column B.

It does **not** define bare `--` on the Hebrew side. An older CrossWire CATSS importer
added bare `--` only as a possible Greek-side minus spelling and marked that addition
as uncertain/probably wrong. That is not sufficient evidence to assign MT-side `--`
a meaning by itself.

## Research question

Determine whether the four MT-side `--` rows are:

1. a legacy/spelling variant of the typed `---` apparent-MT-minus event;
2. a structural placeholder saying that column A has no formal MT equivalent while
   column B supplies a reconstructed Hebrew counterpart;
3. source corruption/typo;
4. or a distinct CATSS category.

The implementation must preserve the raw `--` spelling and stable alignment identity.
No generic zero-MT or generic column-B-only acceptance is allowed.

## Comparative corpus audit

A temporary CI-only audit compares the four `--` rows with all current valid
MT-side `---` apparent-minus rows, including:

- presence/absence of column B;
- `retroversion_kind`;
- MT/LXX cardinality;
- exact column-B prefixes;
- whether any MT-side bare `--` occurs outside the four residual rows.

No production behavior changes are made during this research gate.
