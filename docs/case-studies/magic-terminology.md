# Case study: magical terminology in the Septuagint

This example uses a concrete lexical question to show how the parent Text-Fabric
corpora and CATSS-TF modules complement each other.

Maria Yurovitskaya's 2018 Oxford seminar report, **“Magic in Hebrew and
Greek,”** asks how Hebrew terms connected with magic were rendered in Greek.
The associated seminar talk was titled **“Greek magical terminology in the
Septuagint.”** Her report discusses especially `μάγος`, `γόης`, the
`φαρμακ-` word group, and `ἐπαοιδός`.

Primary source:

- Maria Yurovitskaya, “Magic in Hebrew and Greek,” *Report of the Oxford
  Centre for Hebrew and Jewish Studies 2017–2018*, pp. 41–42:
  https://www.ochjs.ac.uk/wp-content/uploads/2019/02/ochjs-2018-pdf.pdf

The point here is methodological: start from lexical facts in the parent LXX,
use CATSS alignment identity to cross into BHSA, and keep corpus observations
separate from historical or semantic interpretation.

## Corpus versions used

The counts below were checked against the parent profile supported by CATSS-TF
0.1.0:

- CenterBLC/LXX, version `1935`, release `v1.0.1`, commit
  `f32a98eddf7eb239aa73ab863d70381e416d5076`;
- ETCBC/BHSA, version `2021`, release `v1.8.1`, commit
  `b112c161cfd21eae403d51a2733740d8743460e7`;
- CATSS parallel data acquired locally by the user and projected with
  `catss-lxx` and `catss-bhsa`.

No corpus data or generated module is stored in this repository.

## First pass: what is in the Greek parent?

Exact CenterBLC `lex_utf8` counts for the terms used in this example are:

| lemma | occurrences | books |
| --- | ---: | --- |
| `μάγος` | 10 | Dan 2; DanTh 8 |
| `γόης` | 0 | — |
| `φαρμακός` | 13 | Exod 4; Deut 1; Ps 1; Mal 1; Jer 1; Dan 4; DanTh 1 |
| `φάρμακον` | 12 | 2Kgs 1; TobS 5; Wis 1; Sir 2; Mic 1; Nah 2 |
| `φαρμακία` | 8 | Exod 4; Wis 2; Isa 2 |
| `φαρμακεύω` | 3 | 2Chr 1; 2Mac 1; Ps 1 |
| `ἐπαοιδός` | 23 | Exod 5; Lev 3; 1Sam 1; 2Chr 1; Sir 1; Isa 1; Dan 4; DanTh 7 |
| `ἐπαοιδή` | 2 | Deut 1; Isa 1 |

These are parent-corpus counts, before asking whether a word has CATSS
Hebrew-side coverage.

Two results immediately show why scope matters.

### `μάγος`: Old Greek Daniel versus Theodotion

Yurovitskaya writes that `μάγος` occurs only twice in Daniel. A naive search of
the entire CenterBLC parent returns ten tokens. The apparent mismatch disappears
when the two Daniel traditions are kept separate:

- `Dan` (Old Greek): 2 occurrences, Dan 2:2 and 2:10;
- `DanTh` (Theodotion): 8 occurrences.

CATSS-TF deliberately keeps the corresponding CATSS sources separate as
`45.DanielOG.par` and `46.DanielTh.par`. A query that merges them silently
changes the research question.

### `φάρμακον`: the corpus boundary changes the answer

Across the full CenterBLC parent, `φάρμακον` occurs twelve times: six singular
and six plural. The singular examples are in Tobit S, Wisdom, and Sirach.

If the question is restricted to books that can be projected onto BHSA, the
four occurrences are 2Kgs 9:22, Mic 5:11, and Nah 3:4 (twice), and all four are
plural.

So “`φάρμακον` occurs only in the plural” cannot be evaluated without saying
whether “Septuagint” means the entire Greek parent, the Hebrew-Bible translation
corpus, or another defined subset.

## Reproduce the query with Text-Fabric

First materialize both modules as described in
[the integration guide](../integration.md). Assume that they are siblings under
`/work/modules`:

```text
/work/modules/catss-bhsa/
/work/modules/catss-lxx/
```

The following Python code queries Greek lemmas and then follows
`(catss_source, catss_alignment_id)` into BHSA. It never joins corpora by verse
position or by parent node number.

```python
from collections import Counter, defaultdict
from unicodedata import normalize

from tf.app import use

MODULES = "/work/modules"

lxx_app = use(
    "CenterBLC/LXX:v1.0.1",
    checkout="v1.0.1",
    version="1935",
    locations=MODULES,
    modules="catss-lxx",
)
bhsa_app = use(
    "ETCBC/bhsa:v1.8.1",
    checkout="v1.8.1",
    version="2021",
    locations=MODULES,
    modules="catss-bhsa",
)

L = lxx_app.api
H = bhsa_app.api
L_FEATURES = set(L.Fall())
H_FEATURES = set(H.Fall())

TARGETS = {
    normalize("NFC", lemma)
    for lemma in (
        "μάγος",
        "γόης",
        "φαρμακός",
        "φάρμακον",
        "φαρμακία",
        "φαρμακεύω",
        "ἐπαοιδός",
        "ἐπαοιδή",
    )
}


def feature(api, available, name, node):
    if name not in available:
        return None
    return getattr(api.F, name).v(node)


def memberships(api, available, node):
    for suffix in ("", "_2"):
        alignment_id = feature(
            api, available, f"catss_alignment_id{suffix}", node
        )
        if alignment_id is None:
            continue
        source = feature(api, available, f"catss_source{suffix}", node)
        yield source, alignment_id


# Index Hebrew words by the stable CATSS identity shared by both projections.
hebrew_by_alignment = defaultdict(list)
for node in H.F.otype.s("word"):
    for source, alignment_id in memberships(H, H_FEATURES, node):
        hebrew_by_alignment[(source, alignment_id)].append(node)


greek_rows = []
for node in L.F.otype.s("word"):
    lemma = normalize("NFC", L.F.lex_utf8.v(node))
    if lemma not in TARGETS:
        continue

    book, chapter, verse = L.T.sectionFromNode(node)
    greek_rows.append(
        (
            node,
            lemma,
            L.F.word.v(node),
            L.F.nu.v(node),
            book,
            chapter,
            verse,
        )
    )

# Parent-only lexical summary.
by_lemma = Counter(row[1] for row in greek_rows)
by_book = Counter((row[1], row[4]) for row in greek_rows)

for lemma in sorted(TARGETS):
    matching = [(book, n) for (lex, book), n in by_book.items() if lex == lemma]
    print(lemma, by_lemma[lemma], sorted(matching))


# Cross-corpus detail.
for node, lemma, form, number, book, chapter, verse in greek_rows:
    found_membership = False

    for source, alignment_id in memberships(L, L_FEATURES, node):
        found_membership = True
        hebrew_nodes = hebrew_by_alignment.get((source, alignment_id), [])

        hebrew = [
            {
                "node": h,
                "form": H.F.g_word_utf8.v(h),
                "lemma": H.F.lex_utf8.v(h),
            }
            for h in hebrew_nodes
        ]

        print(
            {
                "greek_ref": f"{book} {chapter}:{verse}",
                "greek_form": form,
                "greek_lemma": lemma,
                "number": number,
                "catss_source": source,
                "catss_alignment_id": alignment_id,
                "hebrew": hebrew,
            }
        )

    if not found_membership:
        print(
            {
                "greek_ref": f"{book} {chapter}:{verse}",
                "greek_form": form,
                "greek_lemma": lemma,
                "catss_alignment_id": None,
                "hebrew": [],
                "note": "parent occurrence outside this CATSS projection",
            }
        )
```

The final detail loop is the important part. The Greek word is selected by an
LXX lexical feature, while the Hebrew correspondence comes from CATSS identity.
A missing Hebrew result is evidence about coverage, not an invitation to choose
the nearest Hebrew word in the same verse.

## What the alignment adds

A few source-level correspondences illustrate what becomes available once the
Greek occurrence is connected to CATSS.

### Exodus 7:11

CATSS distinguishes three different expressions in the same verse:

| MT/CATSS expression | Greek expression |
| --- | --- |
| `W/L/MK$PYM` | `καὶ τοὺς φαρμακούς` |
| `XR+MY` | `ἐπαοιδοί` |
| `B/LH+/YHM` | `ταῖς φαρμακείαις αὐτῶν` |

This is more informative than a verse-level co-occurrence search. It tells us
which Hebrew element CATSS treats as the formal equivalent of each Greek item.

### Deuteronomy 18:10–11

The same word field spans adjacent categories:

- `W/MK$P` ↔ `φαρμακός`;
- `XBR` ↔ `ἐπαοιδήν`.

The surrounding passage also contains Greek terms such as
`μαντευόμενος`, `κληδονιζόμενος`, `οἰωνιζόμενος`,
`ἐγγαστρίμυθος`, and `τερατοσκόπος`. This is a good reminder that a
study limited to four Greek roots describes only part of the lexical field.

### Daniel OG 2:2

Three Greek agent nouns are aligned with three different Semitic expressions:

| CATSS MT expression | Greek |
| --- | --- |
| `L/XR+MYM` | `τοὺς ἐπαοιδούς` |
| `W/L/)$PYM` | `καὶ τοὺς μάγους` |
| `W/L/MK$PYM` | `καὶ τοὺς φαρμακούς` |

Running the same query against `DanTh` makes it possible to compare Old Greek
and Theodotion without treating them as one translation.

## A second example: “passing through fire”

Yurovitskaya uses the child-through-fire passages to argue that the boundary
between “magic” and prohibited religion is not transparent. CATSS-TF can verify
the lexical differences on which that interpretation rests:

| passage | MT/CATSS | Greek rendering |
| --- | --- | --- |
| Deut 18:10 | `M(BYR` | `περικαθαίρων` |
| Ezek 16:21 | `B/H(BYR` | `ἐν τῷ ἀποτροπιάζεσθαί` |
| Ezek 23:37 | `H(BYRW` | `διήγαγον`; the fire phrase is `δι' ἐμπύρων` |
| Jer 32:35 MT = Jer 39:35 LXX | `L/H(BYR` | `τοῦ ἀναφέρειν` |

The corpus establishes the different lexical choices and the Jeremiah
versification mapping. Describing one rendering as “magical” and another as
“cultic” requires philological interpretation beyond those scalar facts.

## Which claims can this case study test?

| claim type | status with CATSS-TF |
| --- | --- |
| exact lemma frequency and book distribution | directly testable in the LXX parent |
| `μάγος` occurs twice in Old Greek Daniel | directly testable and supported |
| exact `γόης` is absent | directly testable; exact lemma count is zero |
| which Hebrew expression corresponds to a Greek occurrence | directly testable where both projections exist |
| `ἐπαοιδός` is concentrated in Exodus and later books, especially Daniel | directly testable as distribution |
| later translators “borrowed” `ἐπαοιδός` from the Pentateuch | corpus-supported hypothesis, not proved by distribution alone |
| a rendering has magical rather than cultic semantics | interpretive |
| a Greek word was rare in non-biblical Greek or first appears in a given century | outside CATSS-TF; requires external Greek corpora |
| a translator chose a word because of associations such as snake charming | historical/semantic argument requiring external evidence |

## Coverage traps exposed by the example

1. **Parent LXX is larger than CATSS Hebrew↔Greek coverage.** CenterBLC contains
   books such as Tobit, Wisdom, and Maccabees that do not have a BHSA projection.
   Their Greek lexical occurrences remain valid parent evidence but cannot be
   turned into BHSA correspondences by CATSS-TF.
2. **Sirach is asymmetric.** CATSS has a Sirach parallel source and
   `catss-lxx` can project it, but BHSA has no Sirach parent. Do not interpret
   a missing BHSA join as a failed Greek mapping.
3. **Daniel has two traditions.** `Dan` and `DanTh` must remain separate.
4. **Rahlfs 1935 is one Greek textual base.** A claim depending on a Göttingen
   reading or manuscript variant requires another textual witness.
5. **Lemma and word family are different questions.** Exact `γόης` is absent,
   while the cognate `γοητεία` occurs in 2 Macc 12:24 in the parent corpus.
6. **CATSS alignment is evidence, not semantic annotation.** It records formal
   correspondences and editorial signals; it does not decide whether a practice
   belongs to the modern analytical category “magic.”

## Where to go next

This small study can be extended in several directions:

- expand the lexical field beyond the four highlighted roots, starting from
  Deut 18:10–11 and collecting `μαντεύομαι`, `οἰωνίζομαι`,
  `ἐγγαστρίμυθος`, `τερατοσκόπος`, and their Hebrew correspondences;
- compare Pentateuch, Prophets, and Daniel as separate translation profiles
  rather than treating “the Septuagint” as one translator;
- compare Old Greek Daniel with Theodotion systematically, using the shared
  CATSS source semantics but separate `Dan` / `DanTh` parent nodes;
- combine lexical choice with CATSS translation-technique features, plus/minus,
  retroversion, and transposition evidence;
- add an external diachronic Greek corpus to test claims about rarity,
  chronology, and non-biblical senses;
- classify local contexts only after the corpus extraction step, preserving the
  extracted lexical/alignment facts separately from the semantic labels.

The reusable pattern is:

```text
Greek lexical query
      ↓
CenterBLC/LXX word node
      ↓
(catss_source, catss_alignment_id)
      ↓
CATSS alignment
      ↓
BHSA word node(s) + Hebrew morphology/lexeme
      ↓
aggregate corpus result
      ↓
philological interpretation
```

That separation makes it possible to reproduce the data layer even when
scholars disagree about the final semantic or historical explanation.
