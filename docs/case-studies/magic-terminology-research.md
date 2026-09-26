# Research notes — magical terminology case study

Issue: #41  
Date: 2026-09-26

## Scholarly source

Primary case-study source:

Maria Yurovitskaya, “Magic in Hebrew and Greek,” in the Oxford Centre for Hebrew
and Jewish Studies annual report for 2017–2018, pp. 41–42 (printed pagination),
reporting research from the Oxford Seminar in Advanced Jewish Studies,
*Greek Expanded, Greek Transformed: The Vocabulary of the Septuagint and the
Cultural World of the Translators*.

https://www.ochjs.ac.uk/wp-content/uploads/2019/02/ochjs-2018-pdf.pdf

The related 2018 presentation is listed as “Greek magical terminology in the
Septuagint” / “Magic and Ritual: some Reflections of Greek Religious Practices in
the LXX.”

## Claims to reproduce or delimit

The annual report gives a compact set of claims suitable for a corpus walkthrough:

1. Greek terms common in broader Greek literature — especially `μάγος`, `γόης`,
   and `φαρμακίς / φαρμακεύς` — are practically absent from the Septuagint,
   while `ἐπαοιδός` and `φάρμακος` are widely used.
2. `μάγος` occurs only twice in the Septuagint, both in Daniel.
3. `γόης` is absent from the Septuagint.
4. The `φάρμακον` word-group behaves differently from Classical Greek:
   `φάρμακον` has strongly negative connotations in the Septuagint and is
   described as occurring only in the plural as a synonym of abstract
   `φαρμακεία` (“witchcraft”).
5. `ἐπαοιδός`, rare as a substantive “enchanter” in broader Greek literature,
   becomes a major Septuagint term. Yurovitskaya proposes that Exodus selected it
   because of snake-charming associations and that later translators borrowed the
   Pentateuchal usage, particularly in Daniel.
6. The “passing son/daughter through fire” ritual is rendered in ways she groups
   as alien religious practice in Jer 32:35 [LXX 39:35] and Ezek 23:37, but as a
   magical practice in Ezek 16:21 and Deut 18:11.

## Evidence classes

The notebook must keep three levels separate.

### Directly corpus-testable

- occurrence counts in the supported CenterBLC/LXX parent;
- book / chapter / verse distribution;
- lemma and surface-form distribution;
- grammatical number and other parent morphology when the feature exists;
- CATSS alignment membership and source identity;
- Hebrew parent words reached through the shared `catss_alignment_id`;
- whether Daniel evidence belongs to `DanielOG` or `DanielTh`;
- the Greek and Hebrew lexical material in the selected “passing through fire”
  passages.

### Corpus-supported but interpretive

- whether a lexical choice should be categorized as “magic” rather than
  “prohibited religion”;
- whether `φάρμακον` has a specifically magical sense in a given context;
- whether the distribution of `ἐπαοιδός` shows borrowing from the Pentateuch by
  later translators;
- translator attitude inferred from lexical choice.

The notebook may present the corpus observations relevant to these claims but must
not label the interpretation as mechanically proved by CATSS-TF.

### Outside CATSS-TF evidence

- frequency and semantics in Archaic, Classical, Hellenistic, or Roman Greek
  outside the Septuagint;
- first attestation dates outside the biblical/Jewish-Hellenistic corpus;
- Plato/Strabo/Lucian parallels and the proposed snake-charming motivation.

Those require external Greek corpora and lexicographic evidence.

## Corpus contract for the demonstration

Use exactly the currently supported profiles:

- ETCBC/BHSA `v1.8.1`, Text-Fabric version `2021`;
- CenterBLC/LXX `v1.0.1`, Text-Fabric version `1935`;
- locally materialized `catss-bhsa` and `catss-lxx` from the same CATSS source
  snapshot.

The notebook must not treat parent node numbers as cross-corpus identities.
Cross-projection traversal is only through `catss_alignment_id`.

CenterBLC/LXX contains books for which CATSS parallel alignment and/or a BHSA
projection is unavailable. Therefore:

- whole-LXX Greek frequency queries use the parent LXX directly;
- Hebrew correspondence claims are limited to CATSS/BHSA-supported sources;
- an empty Hebrew join is not automatically an error: it can indicate a Greek
  addition or a source with no BHSA projection.

Both `45.DanielOG.par` and `46.DanielTh.par` are distinct CATSS sources and must
remain separate in tables and discussion.

## Notebook ergonomics audit

The first implementation intentionally uses normal Text-Fabric APIs plus the
existing CATSS-TF features, without introducing a case-study-specific production
helper.

Record friction encountered in these steps:

1. load each parent app with its local CATSS module;
2. discover lexical values without knowing the exact accent convention in advance;
3. retrieve all occurrences of a lemma family;
4. recover one or both CATSS membership lanes from a Greek word;
5. traverse an alignment ID to BHSA word nodes;
6. show Greek and Hebrew reference/form/lemma/morphology side by side;
7. distinguish no-BHSA-coverage from an actual LXX-plus alignment;
8. inspect a whole verse in cases with LXX/MT versification divergence.

If the notebook needs substantial glue for a generally useful operation, file a
narrow follow-up issue rather than silently turning notebook code into an
unreviewed query API.

## Data boundary

The committed notebook should contain code, scholarly references, aggregate
observations, and a small number of ordinary biblical references/forms as needed
for explanation. It must not commit CATSS raw rows, generated modules, parent
corpora, or a large extracted concordance.
