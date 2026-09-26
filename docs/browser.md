# Text-Fabric browser

CATSS-TF modules are ordinary Text-Fabric enrichment modules. They do not define a
separate corpus or web application.

Use the standard app of the parent corpus and add the locally generated CATSS module.

## BHSA + CATSS

If the generated module is:

```text
/work/modules/catss-bhsa/
```

launch the standard BHSA browser with:

```sh
tf ETCBC/bhsa:v1.8.1 \
  --checkout=v1.8.1 \
  --version=2021 \
  --locations=/work/modules \
  --modules=catss-bhsa
```

or use the CATSS-TF convenience wrapper, which executes the same standard TF browser:

```sh
catss-tf browse bhsa /work/modules/catss-bhsa
```

## CenterBLC/LXX + CATSS

```sh
tf CenterBLC/LXX:v1.0.1 \
  --checkout=v1.0.1 \
  --version=1935 \
  --locations=/work/modules \
  --modules=catss-lxx
```

or:

```sh
catss-tf browse lxx /work/modules/catss-lxx
```

Use `--noweb` on the CATSS-TF wrapper when you want Text-Fabric to run its server
without opening the browser automatically.

## Python API

The same module can be loaded through the normal Text-Fabric advanced API.

BHSA:

```python
from tf.app import use

A = use(
    "ETCBC/bhsa:v1.8.1",
    checkout="v1.8.1",
    version="2021",
    locations="/work/modules",
    modules="catss-bhsa",
)
```

LXX:

```python
from tf.app import use

A = use(
    "CenterBLC/LXX:v1.0.1",
    checkout="v1.0.1",
    version="1935",
    locations="/work/modules",
    modules="catss-lxx",
)
```

The parent app still owns text rendering, sections, writing system, and display. CATSS-TF
only contributes additional sparse node features.

## Browser searches

CATSS features are ordinary scalar TF node features and can be used directly in search
templates.

### BHSA examples

LXX omissions corresponding to BHSA words:

```text
word catss_lxx_minus=1
```

One MT element aligned with two Greek lexical elements:

```text
word catss_mt_n=1 catss_lxx_n=2
```

Verses containing one or more Hebrew-empty/LXX-plus CATSS groups:

```text
verse catss_lxx_plus_n
```

Words with a CATSS retroversion:

```text
word catss_retro=1
```

### LXX examples

Greek words belonging to an explicit CATSS LXX-plus alignment:

```text
word catss_lxx_plus=1
```

Greek words in one-to-many MT→LXX alignments:

```text
word catss_tt_cardinality_mt_lxx=one_many
```

Words with remote transposition evidence:

```text
word catss_trans_remote=1
```

### Multiple memberships

Schema v1 supports two explicit CATSS membership lanes on one parent word. Lane 2 uses
the normal `_2` suffix, for example:

```text
word catss_alignment_id_2
```

Use `catss_alignment_n` to find words that have more than one CATSS membership.

## Provenance and raw evidence

The browser/query features are intentionally scalar. Exact raw CATSS rows, arbitrary
source annotations, physical-line provenance, and normalized mapping records remain in
the generated TSV sidecars. They are not packed into JSON or delimiter-separated TF
feature values.

## Why there is no CATSS-TF app directory

A Text-Fabric app is tied to a corpus/warp. CATSS-TF targets two different parent warps:
BHSA and CenterBLC/LXX. Creating a third CATSS-TF corpus app would duplicate or obscure
the parent corpus behavior.

Text-Fabric explicitly supports enrichment modules as extra feature locations, so the
native parent app + CATSS module is the standard architecture.
