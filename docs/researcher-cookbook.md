# First CATSS-TF research session: canonical Text-Fabric

This guide starts with an **executable, deliberately artificial** Hebrew–Greek
alignment sample. It requires no copyrighted CATSS, BHSA or LXX downloads and
leaves no generated corpus in your checkout. It exercises the same public
canonical materializer and query APIs used with user-authorized sources.

For literal CATSS signs consult the
[complete notation dictionary](notation-reference.md). For all canonical
node types, declared features, parent projection suffixes and imports consult
the [complete TF feature/API dictionary](tf-feature-reference.md). For
Libronix user-workflow differences see the
[coverage matrix](libronix-coverage.md).

## 1. Install a runnable Text-Fabric environment

In a clean repository checkout with Python 3.11–3.13, install the
Text-Fabric-enabled package and run the smoke example:

```sh
python -m pip install -e ".[tf]"
python examples/canonical_research_walkthrough.py
```

The script writes two **synthetic** `.par` inputs into a
`TemporaryDirectory`, calls `materialize_corpus`, reloads the generated
standalone `catss` module with `tf.fabric.Fabric`, and invokes the public
query functions. It does not make network requests or persist upstream source
text, and it works when launched from **any current working directory**.

The JSON summary (key order may vary in other JSON implementations) is:

```json
{
  "alignment_groups": 5,
  "false_cross_group_matches": 0,
  "mt_b_as_mt_a_hits": 0,
  "mt_b_context_hits": 1,
  "mt_greek_groups": 2,
  "multi_form_groups": 1,
  "ordered_adjacent_groups": 1,
  "reversed_greek_order_groups": 0,
  "source_documents": 2,
  "source_scoped_groups": 1
}
```

These numbers are *synthetic smoke expectations*, **not corpus statistics**.
The test `tests/test_researcher_quickstart.py` starts a separate Python
process with an otherwise empty working directory and verifies the output.

## 2. Understand what the query returns

The demo's Genesis 1:1 contains separate editorial alignment groups. The
first one has MT-A `MLK DBR` and Greek `BASILEU/S LOGOS`;
a second has MT-A `MLK` and Greek `QEOS`; a third has MT-A
`DBR` and Greek `LOGOS`. There is one additional source line in
Genesis 1:2 carrying contextual reconstructed column B and a second
source (`JoshB`) with another `MLK` / `BASILEU/S` alignment.

The public `find_aligned_groups` search checks whether *one* group
contains the exact MT-A and Greek forms, with an optional exact
`source="01.Genesis.par"` constraint. The two-source result count is 2,
the Genesis-only count is 1. This is **not a word-to-word** translation
edge; a multiword group does not tell you which words correspond.

`find_groups_with_all_forms` uses conjunction/set-membership within
the **same alignment group**:

```python
from catss_tf import find_groups_with_all_forms

groups = tuple(
    find_groups_with_all_forms(
        api,
        mt_forms=("MLK", "DBR"),
        lxx_forms=("BASILEU/S", "LOGOS"),
    )
)
```

To try either code snippet against the **demo** data, place it inside
`run_demo()` in `examples/canonical_research_walkthrough.py`, immediately
after the `api = Fabric(...).loadAll(...)` line and before the `return` statement. The demo closes its temporary directory when
`run_demo()` finishes, so `api` is **not** a variable exposed by the
script to a separate Python session. Alternatively, obtain your own
long-lived `api` by loading a locally materialized corpus, as described
in [canonical-corpus.md](canonical-corpus.md).

On the demo's already loaded `api` this yields one group. Searching
for both Greek `QEOS` and `LOGOS` yields zero even though both
occur in Genesis 1:1: they belong to **different** alignment groups.
Neither query establishes phrase adjacency, grammatical alignment, lemma
identity, or the full Libronix indexed search semantics.

## 3. Keep reconstructed Hebrew separate

The sample's `=;W/KL` in Genesis 1:2 is a CATSS column-B editorial
reconstruction marker. It is searchable through the exact parsed B field:

```python
from catss_tf import find_mt_b_raw_matches

hits = tuple(
    find_mt_b_raw_matches(
        api,
        "W/KL",
        source="01.Genesis.par",
        retro_kind="context",
    )
)
```

The demo finds exactly one raw-context hit. Calling
`find_aligned_groups(api, "W/KL", "LOGOS")` finds **zero** MT-A lexical
matches, since B is never silently upgraded to an attested Hebrew word.
`find_mt_b_raw_matches` uses case-sensitive raw substring matching
after the parser's column split/trim. It is **not** a Libronix
`Reconst:` lexical index, morphology query, or a manuscript attestation.

## 4. Inspect source and reference evidence

The canonical Text-Fabric warp has `alignment` slots, `mt_element`
and `lxx_element` lexical nodes, `annotation` nodes and
`source_line` nodes. After loading an `api` using the `Fabric(...).loadAll()`
pattern in the script, or from your own local corpus, the following pattern
uses **source provenance**, not positional Hebrew/Greek token inference:

```python
for slot in api.F.otype.s("alignment"):
    source = api.F.catss_source.v(slot)
    section = (api.F.book.v(slot), api.F.chapter.v(slot), api.F.verse.v(slot))
    print(source, section, api.F.catss_alignment_id.v(slot))
```

For Qere/Ketiv, Greek references, LXX plus/minus, source-side notes,
transpositions, `I:...` patterns and the precise scope of
`catss_annotation_target`, consult
[canonical-corpus.md](canonical-corpus.md) and
[special-notation.md](special-notation.md).
The [notation dictionary](notation-reference.md) distinguishes `*`
and `[..]` in Sirach from their general meanings.

For manuscript indicators use
`find_sirach_witness_annotations(api, witness=7)` only on an
appropriately loaded Sirach corpus. A marker is **not a manuscript attestation**
of an individual lexical token; witness-to-reading attribution requires
source-grounded evidence ([issue #132](https://github.com/alexsosn/CATSS-TF/issues/132)).
For unresolved translation technique,
`find_unclassified_alignments(api)` returns the recorded reason rather
than assigning a guessed plus/minus event.

## 5. Switch to real, authorized sources

For a user-supplied authenticated **46-file** CATSS parallel snapshot,
follow [integration.md](integration.md) and
[canonical-corpus.md](canonical-corpus.md): validate the source manifest,
materialize the standalone module, reload `catss`, and re-run the exact
query APIs on **actual source spellings**. The real-data CI checks the full
46-file parser/materializer/readback and Agora adapter independently.
Use source filenames and stable alignment IDs for reproducibility; do
not commit licensed `.par` files or generated corpus extracts.

Acquisition must use **authenticated** HTTPS and an independently trusted
CA chain, or user-authorized local inputs. Do not bypass certificate
verification to make a download succeed (see
[issue #44](https://github.com/alexsosn/CATSS-TF/issues/44)).

The two parent-projection modules, `catss-bhsa` and
`catss-lxx`, require separately pinned BHSA 2021 and CenterBLC/LXX 1935
parents. Their nodes have different numeric identities from canonical
alignment nodes. Strict full-source LXX projection remains constrained
by the JoshB lettered-subverse evidence described in
[issue #96](https://github.com/alexsosn/CATSS-TF/issues/96).
A passing **standalone** smoke does not demonstrate the complete
pinned-parent end-to-end workflow.

## 6. Qere/Ketiv and Sirach annotation evidence

Run the second independently tested, **synthetic** CATSS-to-native-TF walkthrough
from the repository checkout, after installing the Text-Fabric extra:

```sh
python -m pip install -e ".[tf]"
python examples/annotation_evidence_walkthrough.py
```

This program makes two tiny temporary source files, `01.Genesis.par`
and `27.Sirach.par`, calls the public `materialize_corpus` API and
reloads the native standalone Text-Fabric `catss` artifact. It does
not download CATSS, BHSA, LXX, Libronix or any manuscript transcription.
The following JSON fields and counts are deterministic expectations for
these invented source lines, **not measurements of historical texts**:

```json
{
  "alignment_groups": 3,
  "invented_annotation_targets": 0,
  "mt_ketiv_nodes": 1,
  "mt_primary_hbk_nodes": 1,
  "mt_qere_nodes": 1,
  "same_mt_word_for_ketiv_qere": 1,
  "sirach_3_independent_oracle": 1,
  "sirach_3_marked": 1,
  "sirach_7_lacking_independent_oracle": 1,
  "sirach_7_lacking_mt_a": 1,
  "sirach_7_lacking_mt_b": 0,
  "sirach_8_marked": 0,
  "sirach_fragmentary_letters": 1,
  "sirach_lacuna_annotations": 1,
  "source_documents": 2
}
```

The Genesis line `*HBK **HBQ` has **one** canonical `mt_element`
node. Its `catss_text` and `catss_ketiv_text` values are `HBK`,
while `catss_qere_text` is `HBQ`. Do not count these as three
independent MT lexical tokens. The parser also records alignment-level Ketiv/Qere
flags, but the Greek `GR` in this fixture is not a pairwise
word-to-word correspondence to both readings. On your own loaded canonical
`api`, retrieve the individual reading surfaces:

```python
for word in api.F.otype.s("mt_element"):
    if api.F.catss_ketiv_text.v(word) == "HBK":
        print(
            api.F.catss_text.v(word),
            api.F.catss_ketiv_text.v(word),
            api.F.catss_qere_text.v(word),
        )
```

The synthetic Sirach 2:13 uses the *source-tested* markers `[..]`,
`3`, `[BN]*` and `>7`. One `3` marks the manuscript Geniza A,
and a separate `>7` is an editorial **reading-lacking** indicator for
witness 7. To inspect the source **annotation occurrences**, run
the following while `api` is still loaded (inside
`run_demo()`, immediately after `Fabric(...).loadAll()`, or in your
own longer-lived TF session):

```python
from catss_tf import find_sirach_witness_annotations

for hit in find_sirach_witness_annotations(api, 3, mode="marked", side="mt_a"):
    print(hit.source, hit.alignment_id, hit.source_side, hit.raw)

for hit in find_sirach_witness_annotations(api, 7, mode="lacking", side="mt_a"):
    print(hit.source, hit.alignment_id, hit.raw, hit.payload)
```

The synthetic smoke cross-checks each public query against a *separate,
source-scoped exhaustive scan* of native TF `annotation` nodes using
`catss_kind`, `catss_raw`, `catss_side` and
`catss_payload`. It also verifies that manuscript 8 does not appear
and that this sample has no `catss_annotation_target` edge. The
`[BN]*` fragment and `[..]` lacuna are distinct raw annotations,
with Sirach-specific meanings; see
[notation-reference.md](notation-reference.md) and the
[full TF feature inventory](tf-feature-reference.md).

A witness marker is **not a manuscript-to-word** attestation edge.
A Greek word in the same editorial alignment is **not a pairwise**
MT-to-Greek lexical association. Missing a marker in this tiny synthetic
source does not imply the absence of the reading in a real historical
manuscript. Source-grounded Sirach witness-to-reading research is
tracked in [#132](https://github.com/alexsosn/CATSS-TF/issues/132).

## 7. Exact source order and adjacency inside one alignment

The existing `find_groups_with_all_forms` requires every form to be present
in a group but does **not** test their order, repetitions or adjacency. To
distinguish these researcher questions, use the public
`find_groups_with_ordered_forms` helper on a loaded **standalone**
alignment-slot `catss` Text-Fabric corpus:

```python
from catss_tf import find_groups_with_ordered_forms

for hit in find_groups_with_ordered_forms(
    api,
    mt_forms=("MLK", "DBR"),
    lxx_forms=("BASILEU/S", "LOGOS"),
    adjacent=True,
    source="01.Genesis.par",
):
    print(hit.source, hit.alignment_id, hit.mt_elements, hit.lxx_elements)
```

In the first synthetic example this finds **one** group; reversing the
Greek query to `("LOGOS", "BASILEU/S")` finds **zero** such groups
when combined with that same MT sequence. The
[executable first-researcher script](../examples/canonical_research_walkthrough.py)
now checks both results in a fresh-process native-TF smoke.

With `adjacent=False` (the default), queried forms must occur in
**increasing distinct positions** inside the original MT-A or Greek
element sequence, but intervening elements are allowed. With
`adjacent=True`, the elements must be consecutive **within that same
editorial CATSS alignment**. Repeating a query spelling requires two
separate source elements: `("MLK", "MLK")` does not match a group
containing only one `MLK` element. With both sides supplied, **both**
ordered predicates must match the same group; MT order is not interpreted
as a pairwise lexical link to Greek order.

The helper respects exact original CCAT spellings, 1-based
`catss_index` ordering, and exact source filenames. It does not
normalize orthography, look at reconstructed MT column B, bridge two
alignment groups even inside the same verse, interpret Greek articles
as grammatical tags, or perform Libronix indexed running-text phrase
search. The independently tested [#158](https://github.com/alexsosn/CATSS-TF/issues/158)
covers reversed sequences, gaps, duplicate forms and cross-group
false positives. Consult [the source-level Libronix
crosswalk](libronix-coverage.md) before describing a result as
Libronix-equivalent.

## Further research recipes and limitations

The [Libronix crosswalk](libronix-coverage.md) distinguishes
supported source queries, partial mappings, unavailable contextual
product notes and UI-only operations. Product keyboard commands,
popup windows, per-word reconstructed Hebrew equivalences and
manuscript-specific attestation edges are not implemented by this
starter script. These are tracked under
[#126](https://github.com/alexsosn/CATSS-TF/issues/126) and
[#151](https://github.com/alexsosn/CATSS-TF/issues/151).

The synthetic demo is a first user-facing executable smoke. A
different researcher-agent still needs to follow the complete
published workflow using independently acquired pinned-parent data
before #151 can be closed.
