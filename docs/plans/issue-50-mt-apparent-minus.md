# Plan — issue #50 MT-column `---` apparent minus

Research basis: [issue-50-mt-apparent-minus.md](../research/issue-50-mt-apparent-minus.md).

## Gate 1 — RED tests

Commit failing behavior tests before production changes:

1. parser: MT-column-A `---` emits exactly one typed
   `apparent_minus` annotation with `mt_a` scope while preserving raw text,
   column-B retroversion, lexical counts and stable alignment identity;
2. directionality: Greek-column `---` remains LXX-minus and does not create an
   MT-apparent-minus annotation;
3. technique: explicit apparent MT minus admits zero-MT/nonempty-Greek cardinality
   without setting `addition_vs_mt` or `omission_vs_mt`;
4. technique: apparent-minus evidence fails closed when MT is nonempty or Greek is
   empty, and unexplained zero-MT/nonempty-Greek still fails;
5. BHSA resolver: apparent-minus alignment gets a distinct verse anchor, never a
   neighboring word mapping and never an `lxx_plus` anchor;
6. BHSA materializer/schema: verse anchor is query-native as
   `catss_apparent_mt_minus_n` and `catss_sem_apparent_minus`, with a typed
   `apparent_mt_minus` sidecar row;
7. LXX materializer: mapped Greek words expose
   `catss_sem_apparent_minus` and `catss_sem_apparent_minus_mt_a`;
8. existing explicit `--+` behavior remains addition-vs-MT and existing Greek
   `---` remains omission-vs-MT;
9. cross-projection consistency accepts exactly the expected apparent-minus asymmetry:
   BHSA verse anchor + LXX word mappings, with no neighboring BHSA word mapping or
   LXX structural anchor.

The RED commit(s) contain no production fix.

## Gate 2 — implementation

Implement the smallest shared semantic change:

- parser helper for exact first-token MT `---` -> existing `apparent_minus`
  semantic identity;
- technique keyword evidence `apparent_mt_minus`, default false for compatibility;
- derive alignment evidence from the typed annotation, not from empty counts;
- BHSA resolver anchor kind `apparent_mt_minus`;
- TF anchor schema/count feature for the BHSA verse;
- standard semantic feature on that verse node;
- cross-projection semantic applicability for `apparent_minus` so Greek memberships
  expose the MT-scoped source judgment;
- materializer sidecar/anchor propagation;
- consistency classification for the typed apparent-minus asymmetry.

Do not:
- change `is_lxx_plus`;
- infer apparent minus from `mt_n == 0`;
- reinterpret Greek-side `---`;
- absorb #52, #53 or the two #54 cardinality outliers.

## Gate 3 — complete-snapshot guard

Replace the verbose research audit with a concise invariant that checks the current
complete snapshot has **63** exact first-token MT-side `---` markers:

- all 63 have exactly one typed `apparent_minus` annotation;
- exactly 61 have zero MT and nonzero Greek lexical count and derive technique
  successfully with `addition_vs_mt=False`;
- the remaining shapes are exactly one `(0, 0)` and one `(1, 2)` alignment;
- both outliers remain fail-closed in technique-v1 and are tracked by #54.

The existing complete notation gate remains.

## Gate 4 — GREEN

Run exact-head:
- ruff check / formatting;
- mypy;
- pytest on Python 3.11, 3.12 and 3.13;
- release smoke;
- complete-CATSS audit.

## Gate 5 — independent adversarial review

Review the exact final green head from scratch, challenging:

- MT/Greek direction confusion for `---`;
- accidental synonymy with `--+`;
- broad matching of dashes inside lexical/annotation content;
- hidden acceptance of unexplained empty-side rows;
- BHSA anchoring to a neighboring word;
- loss of alignment identity/raw provenance;
- semantic scope loss when projected to LXX words;
- anchor collisions or false aggregate counts.

Any behavior finding returns to RED → fix → GREEN → re-review. Merge only after the
exact final head has no blocking findings.

## Downstream acceptance

After merge, merge main into PR #47 and rerun its canonical complete-corpus materializer.
The 61-row admissible apparent-minus class must no longer stop technique derivation.
The two contradictory `---` outliers remain expected downstream blockers for #54;
Sirach and other residual zero-side classes remain owned by #52/#53.
