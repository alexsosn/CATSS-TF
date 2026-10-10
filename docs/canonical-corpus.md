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
| `mt_b_carrier` | one MT-column-B reconstruction carrier when MT-column-A is lexically empty, Greek lexical material is present, **and the row is not already marked LXX-plus**; nonlexical marker values remain markers |
| `lxx_element` | one parsed Greek lexical element |
| `annotation` | one typed CATSS annotation/siglum occurrence |
| `reference` | one structured scalar Greek reference override |
| `reference_range` | one typed contextual Greek reference range with explicit start/end chapter, verse, and subverse |
| `source_line` | one physical CATSS source line owned by the alignment |

Every non-slot node is connected through `oslots` to the alignment slot or slots it
describes. Repeated annotations and source lines remain separate nodes.

## MT-column-B-only reconstructed carriers

When CATSS column A is lexically empty, the Greek side has lexical material,
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
The same holds for ordinary, explicitly marked LXX-plus alignments that
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
