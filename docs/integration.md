# Opt-in real-corpus integration

Normal CATSS-TF CI is intentionally corpus-independent. This procedure exercises the
same production materializers against CATSS data acquired by the user and the exact
supported Text-Fabric parents.

## 1. Install

From a released wheel/package:

```sh
pip install \
  "catss-tf[tf] @ https://github.com/alexsosn/CATSS-TF/releases/download/v0.1.0/catss_tf-0.1.0-py3-none-any.whl"
```

Verify:

```sh
catss-tf --version
# catss-tf 0.1.0
```

## 2. Acquire CATSS

Use an existing local CATSS parallel directory, or fetch directly from the current
upstream CCAT distribution host:

```sh
catss-tf fetch ./data/catss-parallel
catss-tf validate ./data/catss-parallel
```

The user is responsible for the upstream CATSS/CCAT terms.

## 3. Materialize BHSA

```python
from tf.app import use

from catss_tf import TextFabricBhsaProvider, materialize_bhsa
from catss_tf.bhsa_schema import (
    BHSA_CHECKOUT_COMMIT,
    BHSA_CHECKOUT_TAG,
    BHSA_MAX_NODE,
    BHSA_MAX_SLOT,
    BHSA_REPOSITORY,
    BHSA_SECTION_TYPES,
    BHSA_SLOT_TYPE,
    BHSA_VERSION,
    BhsaParentProbe,
)

A = use(
    "ETCBC/bhsa:v1.8.1",
    checkout="v1.8.1",
    version="2021",
)

api = A.api
probe = BhsaParentProbe(
    repository=BHSA_REPOSITORY,
    version=BHSA_VERSION,
    checkout_tag=BHSA_CHECKOUT_TAG,
    checkout_commit=BHSA_CHECKOUT_COMMIT,
    slot_type=BHSA_SLOT_TYPE,
    max_slot=api.F.otype.maxSlot,
    max_node=api.F.otype.maxNode,
    section_types=tuple(api.T.sectionTypes),
    feature_names=frozenset((*api.Fall(), *api.Eall())),
)

assert probe.max_slot == BHSA_MAX_SLOT
assert probe.max_node == BHSA_MAX_NODE
assert probe.section_types == BHSA_SECTION_TYPES

result = materialize_bhsa(
    "./data/catss-parallel",
    "./generated/catss-bhsa",
    provider=TextFabricBhsaProvider(api),
    parent_probe=probe,
)
print(result.summary)
```

Materialization is fail-closed: an existing destination, parent-profile drift, unknown
CATSS source, unresolved mapping, or schema overflow aborts publication.

## 4. Materialize CenterBLC/LXX

```python
from tf.app import use

from catss_tf import TextFabricLxxProvider, materialize_lxx
from catss_tf.lxx_schema import (
    LXX_MAX_NODE,
    LXX_MAX_SLOT,
    LXX_NODE_COUNTS,
    LXX_RELEASE_COMMIT,
    LXX_RELEASE_TAG,
    LXX_REPOSITORY,
    LXX_REQUIRED_FEATURES,
    LXX_SECTION_TYPES,
    LXX_SLOT_TYPE,
    LXX_VERSION,
    LxxParentProbe,
)

A = use(
    "CenterBLC/LXX:v1.0.1",
    checkout="v1.0.1",
    version="1935",
)

api = A.api
node_counts = {node_type: len(api.F.otype.s(node_type)) for node_type in LXX_NODE_COUNTS}
probe = LxxParentProbe(
    repository=LXX_REPOSITORY,
    version=LXX_VERSION,
    release_tag=LXX_RELEASE_TAG,
    release_commit=LXX_RELEASE_COMMIT,
    slot_type=LXX_SLOT_TYPE,
    max_slot=api.F.otype.maxSlot,
    max_node=api.F.otype.maxNode,
    section_types=tuple(api.T.sectionTypes),
    node_counts=node_counts,
    feature_names=frozenset((*api.Fall(), *api.Eall())),
)

assert probe.max_slot == LXX_MAX_SLOT
assert probe.max_node == LXX_MAX_NODE
assert probe.node_counts == LXX_NODE_COUNTS
assert LXX_REQUIRED_FEATURES <= probe.feature_names
assert probe.section_types == LXX_SECTION_TYPES

result = materialize_lxx(
    "./data/catss-parallel",
    "./generated/catss-lxx",
    provider=TextFabricLxxProvider(api, probe),
)
print(result.summary)
```

## 5. Compare both projections

```python
from catss_tf import compare_projection_bundles

report = compare_projection_bundles(
    "./generated/catss-bhsa",
    "./generated/catss-lxx",
)
assert report.ok, report.findings
print(report.summary)
```

The consistency check reads the generated schema-v1 sidecars. It does not need to load
either parent corpus again.

## 6. Browse/query

```sh
catss-tf browse bhsa ./generated/catss-bhsa
catss-tf browse lxx ./generated/catss-lxx
```

These commands invoke the standard Text-Fabric parent apps. See `docs/browser.md` for
direct `tf`/Python equivalents and search examples.

## What to retain for reproducibility

Keep, locally:

- the exact CATSS source directory used;
- the two generated module bundles;
- the materializer software version;
- the parent release/version named above.

Each generated bundle contains source SHA-256 fingerprints and normalized provenance
sidecars. CATSS-TF does not upload these artifacts.
