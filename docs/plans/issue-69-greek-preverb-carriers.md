# Plan — issue #69 zero-token Greek-preverb carriers

Research basis: [issue-69-greek-preverb-carriers.md](../research/issue-69-greek-preverb-carriers.md).

## Gate 1 — RED tests

Add tests before production changes for the three current zero-token carrier shapes:

1. bare `{p}` with lexical MT and zero Greek lexical tokens is accepted by
   technique-v1;
2. `{p} ---` is likewise accepted without becoming an omission;
3. both shapes retain their typed `greek_preverb` annotation;
4. `cardinality_mt_lxx` remains `one_zero` or `many_zero`;
5. `addition_vs_mt=False` and `omission_vs_mt=False`;
6. a generic MT-nonempty / Greek-empty alignment with no typed carrier evidence still
   fails closed;
7. direct `derive_technique_state` coverage proves the exception is controlled by an
   explicit `greek_preverb_carrier` input rather than cardinality alone.

Commit the tests before production changes and confirm the expected failure.

## Gate 2 — implementation

Extend `derive_technique_state()` with a default-false
`greek_preverb_carrier` evidence flag.

In the Greek-empty validation branch, admit the row only when at least one of these
explicit evidence classes is present:

- LXX-minus;
- transposition;
- Greek-preverb carrier.

`derive_alignment_technique()` supplies the flag only from a typed Greek-side
`greek_preverb` annotation.

Do not change parser marker recognition, lexical counting, addition/omission formulas,
or the technique-v1 serialized schema.

## Gate 3 — complete-snapshot guard

Replace the temporary research audit with a permanent guard requiring exactly these
three current MT-nonempty / Greek-empty Greek-preverb carriers:

- `23.Prov.par` Prov 28:18 `B/)XT -> {p} ---`;
- `27.Sirach.par` Sir 5:2 `)XRY 3 -> {p} ---`;
- `27.Sirach.par` Sir 23:17 `B/W 3 -> {p}`.

For each require:

- typed Greek-side `greek_preverb` evidence;
- `is_lxx_minus=False`;
- zero Greek lexical tokens;
- technique derivation succeeds;
- no addition/omission claim.

Any extra current zero-token Greek-preverb carrier should fail the guard.

## Gate 4 — exact-head verification and independent review

Require Python 3.11/3.12/3.13, ruff, format, mypy, release smoke and complete 46-file
audit on the exact final SHA.

Then review independently, trying to falsify:

- accidental generic acceptance of Greek-empty rows;
- implicit conversion of `{p} ---` into omission;
- annotation-side confusion;
- technique schema drift;
- regression of true LXX-minus validation;
- new unguarded zero-token carrier population.

Any blocker returns to RED → implementation → full exact-head verification.
