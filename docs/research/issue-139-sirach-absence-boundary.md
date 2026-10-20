# Issue #139 — Sirach >n numeric-prefix annotation guard

## Research: grounded defect and limits
The canonical source parser currently uses `re.finditer(r">(?:10|[1-9])", cell)` in its `book == "Sir"` branch (src/catss_tf/parser.py). The expression has **no numeric suffix guard**: `>12` yields the false typed annotation `raw=">1", payload="1"` and `>101` yields `raw=">10", payload="10"`. This is independently relevant to the merged #138 API, which faithfully queries the typed annotation rather than reconstructing raw source syntax.

The supplied Emanuel Tov CATSS/Libronix documentation limits numbered Hebrew Sirach witnesses to 1–10. It does not define witnesses 11, 12 or 101. The source-preserving parser must not silently treat their numeric prefixes as documented witnesses. The previous #134 regression already requires ambiguous `HB >12` to remain in MT lexical evidence; it did not check the false typed annotation.

## Plan
1. RED first: test parser outputs for valid 1, 7, 10; invalid/ambiguous 12, 11, 101 and 21; adjacent valid and invalid markers in the same row; source column MT-A vs MT-B; source-sensitive non-Sirach negative case. A valid >n may be attached to a lexical reading, so do **not** enforce whitespace before or after without source evidence.
2. Add a canonical TF round-trip regression using source `27.Sirach.par` and `find_sirach_witness_annotations`, checking that no witness-1/witness-10 lacking hits are created by >12/>101.
3. Minimal Sirach-only regex fix with a **digit** boundary after the whole witness number; no additional normalization, data reordering or new annotation/link type. Preserve raw lexical text/columns and alignment IDs.
4. In the pre-existing ephemeral 46-file CI source step, compare old regex vs corrected regex over raw cells, print only aggregate counts and chapter/verse/physical-line identities; pin actual complete annotation counts. Do not commit or print full source text.
5. Exact-head Python 3.11–3.13, 46-file materialization/reload, release and Agora smoke, independent adversarial review. Keep #132 open: no witness-to-word attribution is implied.

This ticket addresses numeric-prefix overmatching only. It does not decide the validity of suffixed alphabetic strings or cases where tokens are attached to lexical material; those require independent source grammar analysis.

## Empirical source audit and acceptance

On the exact user-authorized ephemeral 46-file source snapshot, [CI run
39448451422](https://github.com/alexsosn/CATSS-TF/actions/runs/39448451422)
measured **92** historical `>n` regexp matches across Sirach source columns
but only **88** matches whose witness number is complete; the new parser
emitted **88** typed `sirach_reading_lacking_in_witness` annotations.
Thus **four** old annotations represented partial numeric matches on real
CATSS data. These were not missing manuscript readings and must not be
counted in witness-absence analyses.

The follow-up CI assertion pins `(legacy, complete, independent-oracle, typed) == (92, 88, 88, 88)`
against the same source snapshot, independently counts full numeric digit runs, and emits only four source locations without
text. All 46 files materialized successfully, the canonical TF corpus
reloaded, and the Agora smoke passed in the discovery run. Source bytes,
lexical cells, reconstructions, and TF generated data remain outside git.
The exact affected witness identities cannot be inferred from aggregate
counts alone; inspect original licensed source with authorized access when
making a philological claim.
