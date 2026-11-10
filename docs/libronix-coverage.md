# Libronix CATSS (2003) → CATSS-TF coverage crosswalk

**Scope.** The project owner provided two 2003 Emanuel Tov / Lexham introductions to the *Parallel Aligned Hebrew-Aramaic and Greek Texts of Jewish Scripture*: the main parallel resource and the resource titled *Alexandrinus and Theodotion Variants*. They have the same introductory explanation and glossary, but different resource titles. Their product-specific indexing and UI instructions are **not** a specification for a drop-in Libronix application.

**Input boundary.** CATSS-TF consumes user-acquired CCAT `.par` source files, not the compiled Libronix resource. A Libronix display label, contextual pop-up, or searchable field may not survive unchanged into the raw CCAT format. Never reconstruct missing editorial notes or manuscript evidence by guessing. Work is tracked in [#126](https://github.com/alexsosn/CATSS-TF/issues/126); this page records the current *known* capabilities and explicit verification gaps, not certification of complete compatibility.

| Requirement from the 2003 introductions | CATSS-TF implementation | Status / boundary |
| --- | --- | --- |
| MT formal correspondences (Hebrew/Aramaic consonantal first line) | Canonical alignment slot, `mt_element`, `catss_mt_col_a`, `catss_mt_raw`; `catss-bhsa` projection against a checked BHSA warp | Implemented as source-preserving data; BHSA token mapping may fail closed |
| Reconstructed Hebrew parent-text reading (second line / column B) | `catss_mt_col_b`, `catss_retro_kind`, scoped `mt_b` annotations; special `mt_b_carrier` for physically empty A | Partial search equivalence: raw B is preserved but not universally tokenized into a distinct lexical corpus; reconstructions are tentative and intentionally incomplete |
| Greek lexical correspondences and ordering | `lxx_element` nodes with `catss_index`; alignment slot order; optional LXX parent projection | Implemented at source-element level; TLG/Libronix surface order and all versification differences require real-data comparisons |
| LXX +/- and apparent or doubtful events | `catss_lxx_plus`, `catss_lxx_minus`, typed `annotation` nodes and technique classifications | Implemented with explicit unclassified/validation states; zero-side rows are not automatically equivalent to translation omissions/additions |
| Transposition, distribution, doublets, repetition, segment changes, infinitive absolute and grammatical/lexical comments | Typed notation catalogue, raw/payload annotations and `catss_sem_*` feature family; selected target edges where source proves exact elements | Implemented for documented and source-encountered forms; full relation/endpoint and source-to-TF coverage remains to be certified under #126 |
| Qere/Ketiv and LXX agreement with a reading | `mt_readings`, `catss_ketiv` / `catss_qere`, named semantic agreement features and source annotations | Implemented for encoded evidence; Libronix pop-up notes are not assumed present in the raw source |
| Samaritan Pentateuch comparisons and apparatus references | `sp` / `sp~` typed semantics; patterned `<sp…>` apparatus annotation | Decoder implemented; full projection feature inventory fixed and merged in [#128](https://github.com/alexsosn/CATSS-TF/pull/128) |
| Distinct Joshua and Judges A/B traditions; Old Greek vs Theodotion Daniel | Separate source identities (`06.JoshB`, `07.JoshA`, `08.JudgesB`, `09.JudgesA`, `45.DanielOG`, `46.DanielTh`) | Supported as independent CATSS documents; the Libronix *variants-only* selection is not claimed to have an identical standalone resource format |
| Sirach Hebrew witnesses, manuscript hands, lacunae and additions | Book-specific notation, witness-number annotations, `sirach_lacuna_or_illegible` distinct from LXX plus | Partially supported: all documented witness labels have decoder kinds, but individual witness-to-reading associations need E2E validation |
| Psalm 151, 1 Esdras and Hebrew reconstruction of Baruch | Separate CCAT source files, first-class alignment groups | Source coverage supported; individual reconstruction completeness remains as supplied by CATSS |
| Greek verse overrides, subverses and contextual ranges | `reference` / `reference_range` nodes preserve spelling and boundaries | Supported as evidence, **not** as automatically verified LXX target edges; JoshB 9:2a–f cannot be projected to six distinct subverses in pinned CenterBLC/LXX; see #96 |
| Rahlfs/Göttingen and Ziegler notes, conjectures | Typed annotations with source/provenance | Only source-provided notes are represented; CATSS-TF does not distribute full critical editions |
| General `*` / `[..]` vs Sirach's different meanings | Book-specific decoder with distinct semantic identities | Declared TF feature inventory repaired in [#128](https://github.com/alexsosn/CATSS-TF/pull/128); real full-source projection gate still required |
| Libronix pop-up note search, keyboard switching, built-in query dialogs, synchronized resource windows | Canonical TF nodes/features, Python and TF search/browser, standard external parent app | **Product UI-only** behavior is not implemented as Libronix UX; reproducible query workflows, not UI imitation, are the goal |

## A source-alignment query corresponding to Libronix `ANDEQUALS`

In the standalone canonical TF corpus, Hebrew and Greek elements are reachable from **the same alignment slot**, rather than by equating foreign node numbers. The following executable sketch retrieves source-level co-memberships; use the exact CCAT spellings observed in `catss_text` (not necessarily Unicode Hebrew/Greek forms).

```python
from catss_tf import find_aligned_groups
from tf.fabric import Fabric

api = Fabric(locations="./generated/catss", silent="deep").loadAll(silent="deep")

# Exact raw CCAT spellings, not automatically Unicode-normalized forms.
for group in find_aligned_groups(api, "MLK", "BASILEU/S", source="01.Genesis.par"):
    print(group.source, group.chapter, group.verse, group.alignment_id)
    print(group.mt_elements, group.lxx_elements)
```

The query is a group-level correspondence query. It does **not** assert word-to-word alignment inside a many-to-many group. Nor does it reproduce Libronix's indexed search or locale-specific Greek/Hebrew wildcard handling. For an exact same-alignment article+noun (or other multi-form) query, use the
public `find_groups_with_all_forms` helper:

```python
from catss_tf import find_groups_with_all_forms

# Replace with exact `catss_text` spellings observed in your local source.
for group in find_groups_with_all_forms(
    api,
    mt_forms=("MLK",),
    lxx_forms=("O(", "BASILEU/S"),
    source="01.Genesis.par",
):
    print(group.chapter, group.verse, group.alignment_id, group.lxx_elements)
```

The query requires **all distinct forms** on their respective sides in one
CATSS alignment slot; Hebrew-only and Greek-only searches also work. Repeated
requested spellings are set-membership, not token multiplicity. Co-membership
does not imply phrase adjacency, running-text order, pairwise lexical matches
or links to reconstructed MT-B forms; such claims need separate evidence.

## Inspect exact raw reconstructed Hebrew (MT column B)

The canonical corpus preserves CATSS's tentative, editorial MT-B column separately from
MT-A lexical elements. To find an **exact, case-sensitive substring of the raw
column-B field**, including B evidence on ordinary MT-A-bearing or marked LXX-plus
alignments, use:

```python
from catss_tf import find_mt_b_raw_matches

# Exact unnormalized CATSS source spelling; not a reconstructed Hebrew lemma.
for hit in find_mt_b_raw_matches(
    api,
    "W/KL",
    source="12.2Sam.par",
    retro_kind="context",
):
    print(hit.group.source, hit.group.chapter, hit.group.verse, hit.group.alignment_id)
    print(hit.mt_b_raw, hit.retro_kind, hit.group.mt_elements, hit.group.lxx_elements)
```

`mt_b_raw` reproduces exactly the canonical `catss_mt_col_b` feature value;
the parser has already split the original MT cell at its first `=` and trimmed
surrounding column-B whitespace. For the complete physical source spelling,
inspect `catss_mt_raw` and the typed `source_line` / `catss_raw` nodes.
`retro_kind` is the existing parser's editorial classification (`context`,
`plain`, `vocalization`, etc.).
Raw substring search includes markup and can match part of a source spelling.
It does **not** tokenize column B, infer a reconstructed lexical occurrence,
identify an attesting Hebrew manuscript, normalize spelling, establish
within-group word-to-word edges, or reproduce Libronix `Reconst:` indexing.
Use exact `source` and `retro_kind` filters where the scope matters;
the query scans one native alignment-slot warp and returns source-ordered groups.
See [issue #126](https://github.com/alexsosn/CATSS-TF/issues/126) for the
remaining lexical-reconstruction and product-equivalence research.

## Verification rules

- A zero-unknown-sigla parser report is **necessary but insufficient**: check the declared feature catalogue, emitted projection TF data and researcher query results as separate gates.
- Match exact source files, version and parent pins before making claims about Greek variants or textual references.
- Annotated manuscript lacunae are not Greek translation additions; an empty reconstructed Hebrew cell is not necessarily missing Greek material.
- Do not silently turn the Libronix variant-only second resource into a complete second independent manuscript text or mix A/B and OG/Theodotion in one undifferentiated sequence.
- No generated CATSS data, critical editions, Hebrew fragments or parent corpora may be committed.

For parser/semantic details see [special-notation.md](special-notation.md), [canonical-corpus.md](canonical-corpus.md), and [integration.md](integration.md). The acceptance matrix and pending empirical checks live in [#126](https://github.com/alexsosn/CATSS-TF/issues/126).
