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
| `lxx_element` | one parsed Greek lexical element |
| `annotation` | one typed CATSS annotation/siglum occurrence |
| `reference` | one structured Greek reference override |
| `source_line` | one physical CATSS source line owned by the alignment |

Every non-slot node is connected through `oslots` to the alignment slot or slots it
describes. Repeated annotations and source lines remain separate nodes.

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
- deterministic translation-technique-v1 cardinality, token-balance,
  addition/omission and transposition facts.

Detailed lexical elements and annotations are nodes rather than delimiter-packed
strings.

## Reference edges

A `reference` node records the structured chapter/verse/subverse information parsed
from CATSS. When its target resolves uniquely to a verse in the same CATSS source,
`catss_reference_target` connects the reference node to that verse node.

No edge is fabricated when the target is absent or ambiguous. CATSS transposition
markers currently do not carry a deterministic target alignment in the parser IR, so
the corpus records their typed semantics without inventing a transposition edge.

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
- exact counts of MT elements, LXX elements, annotations, references and source lines;
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
