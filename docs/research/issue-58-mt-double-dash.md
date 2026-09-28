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


## Complete-snapshot result

The comparative 46-file audit found **five** MT-column-A first-token `--` rows, not
four. Four are the target population from #53; the fifth is a materially different
Sirach 1:19 row:

- target four: `mt_n == 0`, `lxx_n > 0`, column B present;
- Sirach 1:19: `--\t---`, `mt_n == 0`, `lxx_n == 0`, no column B.

Therefore bare MT-side `--` is not globally equivalent to apparent-minus and must not
be typed from the marker alone.

The 61 valid `---` apparent-MT-minus rows provide the comparison population:

- 22/61 also carry column B;
- retroversion kinds among all 61 are: 16 contextual, 4 plain, 2 proper-noun, 39 none;
- their cardinalities are exactly 40 `(0,1)`, 17 `(0,2)`, 4 `(0,3)`.

The four target `--` rows fall entirely inside that already-attested structural
profile: three contextual retroversions and one plain retroversion, all with
`mt_n == 0` and `lxx_n > 0`. No target row has lexical MT material.

## Interpretation

The strongest source-grounded interpretation is that the four target rows are a
legacy/variant surface spelling of the same **apparent MT minus with reconstructed
Hebrew counterpart** represented elsewhere by `--- =...`:

- column A explicitly has no lexical MT element;
- column B supplies a reconstructed Hebrew counterpart;
- Greek supplies the aligned lexical material;
- CATSS documentation assigns column B precisely to presumed Hebrew equivalents behind
  Greek readings that differ from MT.

This is distinct from LXX-plus `--+`: the reconstructed Hebrew counterpart is explicit,
so translation-technique `addition_vs_mt` must remain false.

Because the fifth Sirach `--\t---` row proves that marker spelling alone is ambiguous,
the semantic rule must use the full structural predicate and remain fail-closed outside
it.

## Representation decision

For an alignment whose first MT-column-A token is exactly `--`, emit the existing
typed `apparent_minus` semantic **only when**:

1. MT column B is present and non-empty;
2. MT lexical count is zero;
3. Greek lexical count is positive.

Preserve `raw="--"` on the annotation. Do not set `is_lxx_plus`.

No new semantic synonym is introduced: query users should see the same
`catss_sem_apparent_minus` concept regardless of the legacy raw spelling, while raw
provenance remains available to distinguish `--` from `---`.

The existing apparent-minus technique and projection machinery can then be reused
unchanged. The Sirach 1:19 zero/zero row remains untyped by this rule and continues
fail-closed under its own source semantics.
