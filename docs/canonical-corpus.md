# Canonical CATSS Text-Fabric corpus

CATSS-TF can materialize a standalone Text-Fabric corpus named `catss` directly from
the user-supplied CATSS parallel files. It does not require BHSA or CenterBLC/LXX.

The canonical corpus is the query-native representation of CATSS alignment groups.
The two projection artifacts, `catss-bhsa` and `catss-lxx`, remain feature-only
modules over their parent corpora and share the same stable `catss_alignment_id`.

## Materialize

```python
from catss_tf import materialize_corpus

result = materialize_corpus(
    "./data/catss-parallel",
    "./generated/catss",
)
print(result.summary)
```

Materialization is fail-closed. Parser or notation diagnostics must be resolved or
explicitly allow-listed by code; an allow-listed finding remains preserved in
`catss-diagnostics.tsv`.

The generated corpus is a local derivative of the CATSS data supplied by the user.
CATSS-TF does not distribute generated corpus data.

The canonical corpus preserves any source row that passes parser/notation validation,
even when translation-technique-v1 refuses to classify it. For example, the
complete CCAT snapshot contains a 2 Samuel row with MT-B retroversion only
(`=;W/KL`) and Greek `KAI\\ PA=S`, without MT-A lexical material. The
canonical alignment, provenance and MT-B reading remain first-class; it is
marked `catss_tt_status=unclassified` with the classifier's reason. No
LXX-plus or omission meaning is invented. `catss-technique.tsv` includes only
derived technique rows; the summary's `unclassified_techniques` count and
query-native status/reason feature make this partiality explicit.

## Slot and node model

The Text-Fabric slot type is `alignment`. Every parsed CATSS alignment record has
exactly one slot and carries its stable `catss_alignment_id`.

This choice keeps Hebrew-empty and Greek-empty groups independently addressable. A
plus/minus group therefore does not need a synthetic word or a verse-level packed list.

Additional node types are:

| node type | meaning |
| --- | --- |
| `document` | one CATSS parallel source file |
| `chapter` | chapter structure inside one source |
| `verse` | one CATSS verse/header record |
| `mt_element` | one parsed MT-side lexical element |
| `mt_b_carrier` | one MT-column-B reconstruction carrier when MT-column-A is physically empty, Greek lexical material is present, **and the row is not already marked LXX-plus**; nonlexical marker values remain markers |
| `lxx_element` | one parsed Greek lexical element |
| `annotation` | one typed CATSS annotation/siglum occurrence |
| `reference` | one structured scalar Greek reference override |
| `reference_range` | one typed contextual Greek reference range with explicit start/end chapter, verse, and subverse |
| `source_line` | one physical CATSS source line owned by the alignment |

Every non-slot node is connected through `oslots` to the alignment slot or slots it
describes. Repeated annotations and source lines remain separate nodes.

## MT-column-B-only reconstructed carriers

When CATSS column A is **physically empty** (`catss_mt_col_a == ""`), the Greek side has lexical material,
there is no explicit LXX-plus marker, and the separately marked reconstruction
column B contains evidence, the canonical corpus creates one
`mt_b_carrier` node with `catss_mt_b_raw` (the exact column-B content)
and `catss_retro_kind` (the parser's classification). Its `oslots` points
to exactly one alignment slot. Duplicate-looking source rows remain distinct
carriers by identity and source order.

For example, `=;W/KL` in 2 Samuel 15:18 has raw B `;W/KL` and
`context` kind. `=W/M/BNY` in 1 Esdras 9:33 has raw B
`W/M/BNY` and `plain` kind. `=v` in Ezekiel 4:5 is a
`vocalization` marker **without a Hebrew lexical word**. These three
shapes must never be collapsed into invented MT-A word nodes or construed
as LXX additions. Greek-empty placeholders with column-B marks are **not**
part of this specialized carrier type, even if the raw column B is nonempty.
A column A containing only annotations (such as `^ ^^^`) is **not**
physically empty, even though the parsed MT lexical count is zero, and is
excluded. The same holds for ordinary, explicitly marked LXX-plus alignments that
also have a column-B reconstruction: the existing LXX-plus/retroversion
features retain that source evidence and do not become #59 exceptional nodes.
The complete 46-file CATSS snapshot currently contains
six such carriers, four in 2 Samuel and one each in 1 Esdras and Ezekiel.

Query with `api.F.otype.s("mt_b_carrier")`, then access
`api.F.catss_mt_b_raw.v(node)` and the alignment with
`api.L.d(node, otype="alignment")`. Ordinary column-B annotations on
MT-A-bearing alignments continue to use their established scalar and
annotation features; this scoped node model does not tokenize arbitrary
reconstructions or claim BHSA lexical correspondences.

## Scoped annotation targets

For a CATSS annotation whose typed IR explicitly identifies a lexical target,
the `annotation` node has `catss_target_side` and 1-based
`catss_target_index` features. The canonical
`catss_annotation_target` edge points to the exact lexical child node of
the *same alignment slot*, without referring to foreign BHSA/LXX node IDs.

The researched Jonah 4:3 row `--- YHWH` ↔ `DE/SPOTA KU/RIE` has
one `apparent_minus` annotation written in MT column A but explicitly
targeting Greek element 1 (`DE/SPOTA`). Greek element 2 (`KU/RIE`)
remains unmarked and is the counterpart of MT `YHWH`. The canonical
relation is emitted only for such explicit, validated scopes; neither the
word-count ratio nor the source column implies a target. Unscoped plus/minus
annotations retain their source provenance but have no target edge.

In the TF API:

```python
annotation = ...  # a scoped `annotation` node
target = api.E.catss_annotation_target.f(annotation)[0]
api.F.catss_text.v(target)  # DE/SPOTA for Jonah 4:3
```


## Structural sections

The section hierarchy is:

```text
document -> chapter -> verse -> alignment
```

The Text-Fabric section features are `catss_source,chapter,verse`. Using the CATSS
source filename as the document identity keeps distinct source traditions such as
Joshua A/B and Daniel OG/Theodotion separate.

## Alignment features

Alignment slots expose group-level facts including:

- `catss_alignment_id`, `catss_source`, `book`, `chapter`, `verse`;
- `catss_mt_raw`, `catss_lxx_raw`, `catss_mt_col_a`, `catss_mt_col_b`;
- `catss_mt_n`, `catss_lxx_n` and source-line provenance;
- `catss_lxx_plus`, `catss_lxx_minus`, Ketiv/Qere and transposition flags;
- normalized retroversion kind;
- `catss_tt_status` (`derived` / `unclassified`), with
  `catss_tt_unclassified_reason` for rows whose formal technique cannot be
  inferred safely from the present MT/LXX elements;
- translation-technique-v1 cardinality, token-balance, addition/omission and
  transposition facts **only for derived rows**. The absence of these features
  on unclassified alignments is intentional, not a claim of no addition,
  omission, or transposition.

Detailed lexical elements and annotations are nodes rather than delimiter-packed
strings.

## Sirach manuscript lacunae are not Greek additions

The Hebrew column-A `[..]` marker in `27.Sirach.par` denotes
illegible/missing Hebrew-*witness* text, not the CATSS `--+` LXX-plus
judgment. A row is eligible for derived zero-Hebrew/nonempty-Greek
technique only when the **first MT-A marker** is exactly `[..]`
and an MT-A `sirach_lacuna_or_illegible` annotation is present.
The complete CATSS source scan identifies 4,278 such alignments.
They retain `zero_one`/`zero_many` cardinality and
`token_balance_mt_lxx=not_applicable`, with
`catss_tt_addition_vs_mt` and `catss_tt_omission_vs_mt` both
**not asserted**. An unknown zero-Hebrew row still fails closed.

The standalone canonical corpus keeps a first-class `annotation`
node with `catss_kind=sirach_lacuna_or_illegible`,
`catss_side=mt_a` and raw provenance. Where matching Greek word
memberships exist in the CenterBLC/LXX projection, the associated
Greek word exposes
`catss_sem_sirach_lacuna_or_illegible_mt_a=1`. This annotation
describes the Hebrew witness's state, *not* a translation expansion.
There is no BHSA Sirach parent: no fictitious Hebrew Bible word or
verse anchor is introduced. Reconstructed letters `[]`, mere
physical empty cells, and Greek-side witness annotations are not
silently treated as the `[..]` class.

## Auditing scalar Greek reference candidates

For source-level research without guessing LXX destination nodes, inspect
the local CATSS source with:

```python
from pathlib import Path
from catss_tf.parser import parse_parallel_file
from catss_tf.reference_audit import audit_greek_references
from catss_tf.source import CATSS_PARALLEL_FILENAMES

root = Path("./data/catss-parallel")
report = audit_greek_references(
    parse_parallel_file(root / name) for name in CATSS_PARALLEL_FILENAMES
)
print(report.scalar_references, report.subverse_suffixes)
print(
    report.numeric_candidates_zero,
    report.numeric_candidates_one,
    report.numeric_candidates_multiple,
)
```

This counts **numeric matches to CATSS MT-based source headers** only, not
verified Greek target nodes. A `numeric_candidates_one` record is not a
license to emit `catss_reference_target`: Greek/MT versification and
subverse identities still require pinned parent evidence (issue #96).
No corpus data or generated corpus is distributed by this diagnostic.

## Checking exact pinned LXX parent span availability

After supplying a validated `TextFabricLxxProvider` for the **pinned**
CenterBLC/LXX 1935 v1.0.1 corpus, researchers can audit which explicit
CATSS Greek references have an existing parent verse or labeled subverse
span:

```python
from pathlib import Path
from catss_tf.parser import parse_parallel_file
from catss_tf.parent_reference_audit import audit_lxx_parent_span_availability
from catss_tf.source import CATSS_PARALLEL_FILENAMES

source_root = Path("./data/catss-parallel")
audit = audit_lxx_parent_span_availability(
    (parse_parallel_file(source_root / n) for n in CATSS_PARALLEL_FILENAMES),
    provider,  # configured, pinned TextFabricLxxProvider
)
print(audit)
```

The audit validates the provider's parent metadata and refuses to silently
map `Josh 9:2a` to the unlabeled `Josh 9:2` span. Unsupported and
unknown CATSS sources are counted separately. Missing parent spans
remain missing, and the report does **not** record parent word/node IDs.
A parent span's *existence* is **not evidence that CATSS Greek tokens
align** with that parent span; no `catss_reference_target` edges are
created. The previous MT-header numeric candidate audit is independent
of this Greek-parent availability study. See issue #96 for genuine
textually verified reference destinations.

## Greek-reference textual surface candidates

For a stricter **diagnostic** than the exact LXX parent-span inventory,
compare each explicitly referenced Greek verse with the CATSS alignment's
own Greek tokens using the existing accent-insensitive, non-lemma
normalization functions:

```python
from catss_tf.reference_surface_audit import audit_lxx_reference_surface_candidates

surface = audit_lxx_reference_surface_candidates(
    (parse_parallel_file(source_root / n) for n in CATSS_PARALLEL_FILENAMES),
    provider,  # exact pinned CenterBLC/LXX TextFabricLxxProvider
)
print(surface)
```

The aggregate distinguishes one exact contiguous candidate, multiple
occurrences, no matching sequence, Greek-token-free references,
normalization obstacles, missing parent spans and unsupported sources.
For locally unique occurrences, `exact_single_with_overlap` counts those
whose candidate **word-offset interval** intersects at least one
candidate interval from a *different* alignment in the same source and
exact Greek parent key (including another alignment's ambiguous matches).
`exact_single_without_overlap` is the complementary count, and they sum
to `exact_single`. The overlapping class is divided further:
`exact_single_with_unavoidable_overlap` means at least one competing
alignment has **no disjoint alternative candidate interval**, whereas
`exact_single_with_avoidable_overlap_only` means every competitor has
at least one disjoint alternative despite an overlapping possibility.
These two classes sum to `exact_single_with_overlap`. This is only
**pairwise candidate necessity conditional on placing both alignments**:
multiple competitors can still conflict globally, and the notation itself
may not demand placement. Multiple scalar references on the same alignment
do not compete with themselves; separate CATSS source traditions are counted
independently even where parent book/verse keys coincide.

For each source and exact pinned Greek-parent reference key, the audit
also forms **explicit-reference candidate groups**: one task per distinct
alignment ID, even when a row repeats the same scalar reference. A bounded
(up to 10,000 explored states per group) non-overlapping interval search
classifies each group as `joint_unique_groups` (exhaustively one full
candidate assignment), `joint_multiple_groups` (at least two assignments),
`joint_impossible_groups` (exhaustively no full assignment),
`joint_incomplete_groups` (at least one referenced alignment has no valid
candidate, including missing parents or unsupported lexical normalizations),
or `joint_indeterminate_groups` (the search budget was exceeded).
The search uses lazy iterative depth-first iterator frames: the active
frontier is proportional to assignment depth rather than the number of
candidate alternatives, with a 10,000-visited-state limit per group.
**Input candidate intervals and deterministic sorted alternatives still
consume memory proportional to input size**; the visit budget is not an
overall memory or CPU limit on input normalization and sorting.
These original five `joint_*` categories partition `reference_groups`.
A second **conditional default-context** view includes lexical alignments
without any scalar Greek reference or typed contextual range, assigning
them to the policy-derived default Greek book/chapter/verse from the MT
header. Each implicit lexical row is an additional mandatory candidate
task **only when its exact default parent key already has an explicit
reference group**. `context_groups_with_implicit` counts how many
explicit groups had such contenders. The five `context_*_groups`
outcomes independently partition the same `reference_groups`:
unique, multiple, impossible, incomplete, and indeterminate. A missing,
non-normalizable, or unmatched implicit contender makes the corresponding
context incomplete; Greek-empty placeholders and typed contextual ranges
do not become lexical tasks.

The pinned 46-source CenterBLC/LXX audit finds **279 of 671**
explicit groups with eligible implicit lexical contenders. Original
explicit-only classes are 326 unique, 70 multiple, 19 impossible, 256
incomplete, 0 indeterminate; conditional default-context classes are
**252 unique, 75 multiple, 49 impossible, 295 incomplete, 0
indeterminate**. All counts refer to the same 671 groups and do not
establish a verified semantic Greek target.

The three views are deliberately kept separate. A group classed as
unique by the explicit-only view may become impossible or incomplete
when the hypothesized implicit contenders are included. A third
`role_context_*` partition adds the production LXX resolver's *narrow*
typed transposition exception: two different lexical alignments may
share **identical** Greek word intervals only when one has the
`transposition_alignment` annotation role and the other has the
`transposition_carrier` annotation role. Partially overlapping spans,
ordinary rows, two carriers, two transposition alignments and a third
ordinary contender still conflict. Both annotation roles come from
the parsed CATSS row (not raw Greek string equality). The five
`role_context_*` classes partition the **same 671** explicit groups;
`role_context_groups_with_eligible_pair` counts groups containing
both roles, and `role_context_changed_groups` counts groups whose
outcome differs from the strict default-context view.

In the exact pinned 46-file corpus, **96** of the 671 groups contain
both transposition roles and **17** conditional group outcomes change:
the strict-context 252 unique / 75 multiple / 49 impossible /
295 incomplete / 0 indeterminate become **260 unique / 84 multiple /
32 impossible / 295 incomplete / 0 indeterminate** under the role-aware
rule. All 17 newly feasible groups were previously conditionally
impossible: eight now have one assignment, nine have multiple.
This does not establish Greek reference target semantics.

This is a **third conditional hypothesis**, not a revision of previous
scalar, `joint_*` or `context_*` results. The default Greek location
itself is not a verified reference destination; cross-key interactions,
implicit empty placeholders and source-notation interpretation remain
unmodeled. No new Text-Fabric mappings or
`catss_reference_target` edges are created.

Every input document must have a **distinct CATSS source filename**: the audit rejects repeated
`source_name` values with `ValueError`, including identical or empty
documents, because its candidate scopes rely on unique file provenance.
It does not automatically combine or rename source fragments. None of
these counts proves translation reference semantics:
**full cross-reference constraints are not included**; implicit
lexical rows and typed transposition exceptions are included only in
their separate conditional views, not in the original explicit-only
counts. A unique candidate assignment is not a verified Text-Fabric
target.

The report includes **no raw source text, Greek parent word IDs, or
canonical target edges**. Neither a local `exact_single` match nor an
`exact_single_without_overlap` match is a verified reference destination:
contextual references, implicit (unreferenced) alignment tasks, and
joint-placement constraints may still prevent any one-to-one mapping.
Follow the existing LXX resolver's stricter full-document validation
before proposing any canonical `catss_reference_target` relation. See
`docs/research/issue-96-reference-surface-candidates.md`,
`docs/research/issue-96-overlap-triage.md`,
`docs/research/issue-96-pairwise-necessity.md`,
`docs/research/issue-96-joint-candidate-feasibility.md`,
`docs/research/issue-96-duplicate-source-provenance.md`,
`docs/research/issue-96-memory-bounded-dfs.md`,
`docs/research/issue-96-implicit-context-feasibility.md`,
`docs/research/issue-96-transposition-role-feasibility.md` and issue #96.

## Reference edges

A `reference` node records the exact scalar Greek-side chapter, verse, subverse
and raw spelling parsed from CATSS. The canonical corpus deliberately does not
emit `catss_reference_target` edges: its `verse` sections follow the MT-based
CATSS source headers, so a matching numeric label is **not** a verified Greek
reference target. Referring from one independently sourced Greek text to another
requires a separately grounded resolver (see issue #96).

A typed range such as `[[9.2a-2f]]` is kept as a separate `reference_range`
node attached to its alignment slot. Query-native `catss_range_start_*`
and `catss_range_end_*` features and `catss_raw` preserve both endpoints
without creating six fictitious LXX parent nodes or reducing the range to
scalar endpoints.

Typed scalar references and ranges remain queryable through their node features
and links to alignment slots through `oslots`. No cross-versification target
is inferred from chapter/verse number coincidence. CATSS transposition markers
likewise remain typed but without invented target alignment edges.

## Load with Text-Fabric

```python
from tf.fabric import Fabric

TF = Fabric(
    locations="./generated",
    modules=("catss",),
    silent="deep",
)
api = TF.loadAll(silent="deep")
```

Examples:

```python
# All independent LXX-plus alignment groups.
api.S.search("alignment catss_lxx_plus=1", silent="deep")

# Stable identity and section of an alignment slot.
slot = 1
api.F.catss_alignment_id.v(slot)
api.T.sectionFromNode(slot)

# Lexical/detail nodes belonging to the alignment.
api.L.u(slot, otype="mt_element")
api.L.u(slot, otype="lxx_element")
api.L.u(slot, otype="annotation")
```

The canonical corpus can be loaded without either parent corpus. To move into BHSA or
CenterBLC/LXX, join through `catss_alignment_id` exposed by the corresponding
projection module.

## Preservation audit

Every materialization performs an in-memory preservation audit before the destination
is published. It checks:

- exactly one alignment slot per parser IR alignment;
- exact stable-ID order and uniqueness;
- exact counts of MT elements, LXX elements, annotations, scalar references,
  contextual reference ranges and source lines;
- no child nodes on a lexical side that is actually empty;
- every non-slot node has valid `oslots`;
- source manifest order matches the parsed documents.

CI additionally runs the same materializer over the complete configured 46-file CATSS
snapshot. Known parser-quality diagnostics remain explicit and are preserved rather
than silently dropped.

## Schema version

The standalone corpus uses `@catssCanonicalSchema=1`. This version is independent of
projection schema v1, because the projection modules have a different warp and node
contract.
