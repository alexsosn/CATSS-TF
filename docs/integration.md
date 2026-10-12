# Opt-in real-corpus integration

Normal CATSS-TF CI is intentionally corpus-independent. This procedure exercises the
same production materializers against CATSS data acquired by the user and the exact
supported Text-Fabric parents.

## 1. Install

From the current source (including GitHub-capable Text-Fabric):

```sh
pip install \
  "catss-tf[tf] @ git+https://github.com/alexsosn/CATSS-TF.git"
```

The previously published v0.1.0 wheel has older dependency metadata.
For that wheel, also install `text-fabric[github]>=13.1,<14` explicitly
before downloading pinned BHSA/LXX parents. These corpora are not included.

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
# Only for an independently authenticated CA chain / HTTPS origin:
catss-tf fetch ./data/catss-parallel --ca-bundle ./trusted-upstream-ca.pem
catss-tf fetch ./data/catss-parallel --base-url https://validated.example.org/parallel
catss-tf validate ./data/catss-parallel
```

The user is responsible for the upstream CATSS/CCAT terms.

**Verified TLS:** Some clean Ubuntu/OpenSSL clients currently reject the CCAT
server's incomplete certificate chain. The downloader does not weaken TLS or
fall back to HTTP. `--ca-bundle` uses a PEM file obtained and verified via
an **independent trustworthy channel**, not a certificate scraped from an
unverified CCAT session. `--base-url` must be an HTTPS endpoint whose
identity and upstream data/license provenance you have independently checked;
redirects cannot downgrade to HTTP or switch hostname. Without either,
use an already acquired local directory. Neither option guarantees that the
broken default upstream chain is fixed; see issue #44 for live verification.


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

**Limitation for the complete current CATSS snapshot:** JoshB 9:2 contains
`[[9.2a-2f]]`, but the supported CenterBLC/LXX release has only one
unlabeled Josh 9:2 subverse node. After contextual-range support is enabled,
materializing the *entire* CATSS snapshot against this pinned LXX release
fails with `missing_lxx_reference_range_member`, and no partial module is
published. Synthetic range tests demonstrate the feature contract only;
they do not establish that the pinned parent can represent these six targets.
Preservation in the canonical corpus is tracked by #40 / PR #47.
See [special notation](special-notation.md#contextual-greek-reference-ranges).

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

## Agora's executable standalone adapter

The root `agora.materializer.json` declares one user-local and
network-denied `catss-canonical` producer. Its `catss_tf.agora_adapter` module
accepts `{source} --output {output}` and requires the host to create a
**real empty output directory**. Native `materialize_corpus` builds a
separate absent-path child within staging; only validated flat `.tf` and
`.tsv` files are published to the host's output by no-replace hard links.
The adapter fails on source/output overlap, hostile native outputs,
validation errors and partial hard-link publication, and removes private
staging files on failure. The host retains responsibility for the final
sandboxed transaction and parent-independent Text-Fabric load.

The registered Agora producer invokes this adapter **without** any
`--allow` flags. This is deliberately stricter than the earlier
opt-in native research workflow, which supplied three possible
diagnostic allowances despite reporting **zero actually ignored findings**
in its 46-file run. Direct operators may explicitly pass repeatable
`--allow CODE` for reviewed source anomalies; no such exception is
silently granted to user-local input. Unknown annotations/sigla block
publication, and any explicitly acknowledged diagnostics remain in the
local TSV audit.

The adapter never fetches CATSS or installs a parent corpus. Registration is
not implied by the manifest: Agora must pin an immutable reviewed CATSS-TF
commit, obtain explicit code execution approval and verify the user-local
input license and output permissions. The root manifest currently exposes
**only the standalone canonical corpus**; BHSA/LXX feature-module registration
requires separate reviewed parent bindings and remains unresolved under
CATSS-TF #16 / Agora #221. The standalone corpus is not a substitute for
either projection.

## What to retain for reproducibility

Keep, locally:

- the exact CATSS source directory used;
- the two generated module bundles;
- the materializer software version;
- the parent release/version named above.

Each generated bundle contains source SHA-256 fingerprints and normalized provenance
sidecars. CATSS-TF does not upload these artifacts.
