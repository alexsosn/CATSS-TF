# Plan — issue #67 Greek-side `--+` exact repairs

Research basis: [issue-67-greek-side-plus-repairs.md](../research/issue-67-greek-side-plus-repairs.md).

## Gate 1 — RED tests

Before production changes, add deterministic tests for all six exact rows requiring:

1. `lxx_raw` and physical `raw_lines` remain the original `--+` spelling;
2. semantic parsing sees Greek `---` and therefore `is_lxx_minus=True`;
3. MT lexical count stays positive and Greek lexical count stays zero;
4. technique-v1 derives `omission_vs_mt=True` and `addition_vs_mt=False`;
5. exactly one `source_repair` annotation is emitted on side `lxx`, with raw source
   Greek cell and corrected semantic Greek cell;
6. Prov 30:32 still emits the independent `apparent_plus_minus` annotation;
7. Jer 51:57 still parses contextual reference `[28.57]`;
8. alignment id remains derived from original source bytes;
9. same cells at a different reference do not repair.

Commit the tests before implementation and confirm the expected failure.

## Gate 2 — implementation

Refactor the internal source-repair record to be side-aware and allow both MT and Greek
semantic cell replacements.

Maintain separate closed tables:

- existing exact MT-side repairs;
- six exact Greek-side repairs from #67.

`_parse_physical_row()` keeps source cells separately from semantic cells.
`_build_alignment()` emits provenance annotations from the side-aware repair records.

Do not change technique-v1 or the generic marker vocabularies.

## Gate 3 — complete-snapshot guard

On the current 46-file snapshot assert:

- exactly six distinct `lxx` source repairs from the #67 table;
- each repaired row has `is_lxx_minus=True`;
- no repaired row has `is_lxx_plus=True`;
- no current MT-nonempty/Greek-empty residual remains with raw Greek first token
  `--+`.

Keep all existing notation, continuation and source-repair guards.

## Gate 4 — exact-head GREEN and independent review

Require on the exact final SHA:

- Python 3.11/3.12/3.13 pytest;
- ruff check and format;
- mypy;
- release smoke;
- complete CATSS audit;
- BHSA projection regression proving the LXX-side repair is query-native as
  `catss_sem_source_repair_lxx` with semantic payload on the mapped MT word.

Then perform an independent adversarial review focused on:

- accidental global reinterpretation of Greek-side `--+`;
- wrong-side provenance;
- loss of decorators/references;
- raw-source or alignment-id drift;
- regression of existing MT-side source repairs;
- any technique change beyond the six corrected identities.

Any blocking finding returns to RED → implementation → full exact-head verification.
