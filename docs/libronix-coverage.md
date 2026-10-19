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
| Samaritan Pentateuch comparisons and apparatus references | `sp` / `sp~` typed semantics; patterned `<sp…>` apparatus annotation | Decoder implemented; full projection feature inventory fixed in [#128](https://github.com/alexsosn/CATSS-TF/pull/128) (pending review at time of writing) |
| Distinct Joshua and Judges A/B traditions; Old Greek vs Theodotion Daniel | Separate source identities (`06.JoshB`, `07.JoshA`, `08.JudgesB`, `09.JudgesA`, `45.DanielOG`, `46.DanielTh`) | Supported as independent CATSS documents; the Libronix *variants-only* selection is not claimed to have an identical standalone resource format |
| Sirach Hebrew witnesses, manuscript hands, lacunae and additions | Book-specific notation, witness-number annotations, `sirach_lacuna_or_illegible` distinct from LXX plus | Partially supported: all documented witness labels have decoder kinds, but individual witness-to-reading associations need E2E validation |
| Psalm 151, 1 Esdras and Hebrew reconstruction of Baruch | Separate CCAT source files, first-class alignment groups | Source coverage supported; individual reconstruction completeness remains as supplied by CATSS |
| Greek verse overrides, subverses and contextual ranges | `reference` / `reference_range` nodes preserve spelling and boundaries | Supported as evidence, **not** as automatically verified LXX target edges; JoshB 9:2a–f cannot be projected to six distinct subverses in pinned CenterBLC/LXX; see #96 |
| Rahlfs/Göttingen and Ziegler notes, conjectures | Typed annotations with source/provenance | Only source-provided notes are represented; CATSS-TF does not distribute full critical editions |
| General `*` / `[..]` vs Sirach's different meanings | Book-specific decoder with distinct semantic identities | Declared TF feature inventory defect identified and addressed in [#128](https://github.com/alexsosn/CATSS-TF/pull/128); real full-source projection gate still required |
| Libronix pop-up note search, keyboard switching, built-in query dialogs, synchronized resource windows | Canonical TF nodes/features, Python and TF search/browser, standard external parent app | **Product UI-only** behavior is not implemented as Libronix UX; reproducible query workflows, not UI imitation, are the goal |

## A source-alignment query corresponding to Libronix `ANDEQUALS`

In the standalone canonical TF corpus, Hebrew and Greek elements are reachable from **the same alignment slot**, rather than by equating foreign node numbers. The following executable sketch retrieves source-level co-memberships; use the exact CCAT spellings observed in `catss_text` (not necessarily Unicode Hebrew/Greek forms).

```python
from tf.fabric import Fabric

api = Fabric(locations="./generated/catss", silent="deep").loadAll(silent="deep")

def elements(slot, side):
    nodes = api.L.u(slot, otype=f"{side}_element")
    return tuple(
        api.F.catss_text.v(node)
        for node in sorted(nodes, key=api.F.catss_index.v)
    )

def aligned_pairs(hebrew_source, greek_source):
    for slot in api.F.otype.s("alignment"):
        hebrew = elements(slot, "mt")
        greek = elements(slot, "lxx")
        if hebrew_source in hebrew and greek_source in greek:
            yield api.F.catss_alignment_id.v(slot), hebrew, greek

# Replace with actual CCAT forms, e.g. from a specific alignment:
# list(aligned_pairs("MLK", "BASILEU/S"))
```

This is a group-level correspondence query. It does **not** assert word-to-word alignment inside a many-to-many group. Nor does it reproduce Libronix's indexed search or locale-specific Greek/Hebrew wildcard handling. Article + noun membership in one group can similarly be tested by requiring both Greek forms in `greek`; strict adjacency and textual running order require separate tests.

To compare MT against reconstructed Hebrew, use `api.F.catss_mt_col_a` and `api.F.catss_mt_col_b` on alignment slots. These are raw evidence strings: an MT-B lexical query like Libronix `Reconst:` cannot yet be presumed equivalent to a regularized token search. Query scopes and raw source provenance are distinct from semantic/morphological inference.

## Verification rules

- A zero-unknown-sigla parser report is **necessary but insufficient**: check the declared feature catalogue, emitted projection TF data and researcher query results as separate gates.
- Match exact source files, version and parent pins before making claims about Greek variants or textual references.
- Annotated manuscript lacunae are not Greek translation additions; an empty reconstructed Hebrew cell is not necessarily missing Greek material.
- Do not silently turn the Libronix variant-only second resource into a complete second independent manuscript text or mix A/B and OG/Theodotion in one undifferentiated sequence.
- No generated CATSS data, critical editions, Hebrew fragments or parent corpora may be committed.

For parser/semantic details see [special-notation.md](special-notation.md), [canonical-corpus.md](canonical-corpus.md), and [integration.md](integration.md). The acceptance matrix and pending empirical checks live in [#126](https://github.com/alexsosn/CATSS-TF/issues/126).
