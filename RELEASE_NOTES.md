# CATSS-TF 0.1.0

CATSS-TF 0.1.0 is the first standalone software release for projecting the CATSS
Hebrew–Greek parallel alignment onto existing Text-Fabric corpora.

## What it provides

- `catss-bhsa`: CATSS annotations on ETCBC/BHSA 2021 word/verse nodes;
- `catss-lxx`: CATSS annotations on CenterBLC/LXX 1935 word/reference nodes;
- shared stable CATSS alignment identities and normalized provenance sidecars;
- query-native scalar features for plus/minus, cardinality, retroversion,
  Ketiv/Qere, transposition, strategy annotations, and technique-v1 facts;
- fail-closed mapping and cross-projection consistency checks;
- standard Text-Fabric browser usage through the parent corpus apps.

## Exact parent contracts

- ETCBC/BHSA: TF `2021`, release `v1.8.1`;
- CenterBLC/LXX: TF `1935`, release `v1.0.1`.

Generated modules are valid only for the parent warp/profile against which they were
materialized.

## Data and licenses

This release contains CATSS-TF software only.

CATSS source data, BHSA, and CenterBLC/LXX remain governed by their own upstream terms.
Users are responsible for acquiring and using those datasets accordingly. The MIT
license in CATSS-TF does not relicense any upstream corpus or generated derivative data.

## Known v0.1 limitations

- BHSA projection intentionally excludes 1 Esdras, Psalm 151, Sirach, and Baruch
  because BHSA has no corresponding parent book.
- LXX projection intentionally excludes Joshua A and Judges A because CenterBLC/LXX
  v1.0.1 does not provide separate A-tradition parents.
- schema-v1 supports at most two explicit CATSS membership lanes on one parent word;
  overflow fails closed instead of becoming a packed list.
- technique-v1 does not claim Hebrew↔Greek lemma identity or morphology equivalence,
  and token-count differences are not labeled semantic expansion/contraction.
- unresolved/ambiguous source or mapping structures fail materialization unless an
  explicitly allow-listed validation code is designed to be ignorable.
- real-corpus integration is opt-in and runs on user-acquired data; public CI uses
  synthetic fixtures only.

## Browser

CATSS-TF does not ship a third web app. Use the standard Text-Fabric app/browser for
BHSA or CenterBLC/LXX and add the locally generated CATSS module. See
`docs/browser.md`.

## Installation

Core:

```sh
pip install catss-tf
```

With Text-Fabric integration:

```sh
pip install "catss-tf[tf]"
```

The GitHub release also attaches source and wheel distributions.
