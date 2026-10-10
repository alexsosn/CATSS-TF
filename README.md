# CATSS-TF

CATSS-TF materializes the CATSS Hebrew–Greek parallel alignment as Text-Fabric.

The intended outputs are three locally generated artifacts:

- `catss` — standalone canonical CATSS corpus with alignment groups as first-class nodes;

- `catss-bhsa` — CATSS alignment annotations attached to nodes of ETCBC/BHSA;
- `catss-lxx` — the same canonical CATSS alignments projected onto nodes of CenterBLC/LXX.

This repository does **not** distribute BHSA, LXX, raw CATSS data, or generated TF corpora. It contains software, mapping profiles, tests, and documentation needed to build modules from data acquired by the user under the relevant upstream terms.

## Status

CATSS-TF 0.1.0 is the first standalone release. It includes both CATSS projections,
cross-projection consistency checks, translation-technique v1, and standard Text-Fabric
browser integration.

Install core software:

```sh
pip install \\
  https://github.com/alexsosn/CATSS-TF/releases/download/v0.1.0/catss_tf-0.1.0-py3-none-any.whl
```

Install with Text-Fabric integration from current source (including the GitHub backend):

```sh
pip install \\
  "catss-tf[tf] @ git+https://github.com/alexsosn/CATSS-TF.git"
```

The already-published v0.1.0 wheel retains its original dependency metadata.
If using that wheel, additionally run `pip install "text-fabric[github]>=13.1,<14"`
for BHSA/LXX downloads; a future release will include the fix automatically.

Verify:

```sh
catss-tf --version
```

Read:

1 [docs/canonical-corpus.md](docs/canonical-corpus.md) — standalone CATSS corpus and node model
1 [docs/integration.md](docs/integration.md) — opt-in real-corpus materialization
1 [docs/browser.md](docs/browser.md) — standard Text-Fabric browser/search
1 [docs/case-studies/magic-terminology.md](docs/case-studies/magic-terminology.md) — worked Hebrew↔Greek lexical case study
1 [CHANGELOG.md](CHANGELOG.md)
1 [research.md](research.md)
1 [design.md](design.md)
1 [plan.md](plan.md)
1 [AGENTS.md](AGENTS.md)

## Architectural boundary

CATSS is the source of alignment semantics. BHSA and LXX remain the owners of their node identities and linguistic annotation.

The standalone `catss` corpus owns a Text-Fabric warp whose slot type is
`alignment`. Every CATSS alignment group is therefore independently queryable,
including groups with an empty Hebrew or Greek side.

The two projection modules remain weft-only collections of additional features built
around an existing parent warp. They do not create nodes in BHSA or LXX. Both attach
the same stable `catss_alignment_id` used by the canonical corpus.

The materialization model is:

```text
CATSS source acquired by user
          |
          v
canonical CATSS alignment IR
      /          |          \
     v           v           v
  catss       resolve      resolve
 standalone    Hebrew       Greek
 TF corpus       |           |
                 v           v
             catss-bhsa  catss-lxx
             TF module   TF module
```

## License

The software in this repository is MIT licensed. CATSS data and the parent corpora have separate upstream terms. See [LICENSE_SCOPE.md](LICENSE_SCOPE.md).


## CATSS source contract

The initial release consumes a local directory of CATSS parallel `.par` files. Users may point CATSS-TF at an existing directory or explicitly fetch the files directly from the upstream CCAT host:

```sh
catss-tf fetch ./data/catss-parallel
```

CATSS morphology files are not required.

The user is responsible for the upstream CATSS/CCAT terms that apply to acquisition and use. CATSS-TF does not redistribute the downloaded corpus. The local source directory is fingerprinted by filename, byte size, and SHA-256 before parsing, and repository tests use synthetic fixtures only.

See [research.md](research.md), [design.md](design.md), and [LICENSE_SCOPE.md](LICENSE_SCOPE.md) for the rationale and data-license boundary.


## Text-Fabric browser

CATSS-TF does not implement a separate web application. Generated modules are loaded
into the standard Text-Fabric app/browser of their parent corpus:

```sh
catss-tf browse bhsa ./generated/catss-bhsa
catss-tf browse lxx ./generated/catss-lxx
```

The wrapper validates module/parent metadata and then invokes the normal `tf` browser.
You can also use the direct Text-Fabric `--locations/--modules` mechanism or
`tf.app.use()`.

See [docs/browser.md](docs/browser.md) for exact pinned commands and search examples.


## Public Python API

v0.1 freezes the following package-level entry points:

```python
from catss_tf import (
    TextFabricBhsaProvider,
    TextFabricLxxProvider,
    compare_projection_bundles,
    materialize_bhsa,
    materialize_corpus,
    materialize_lxx,
)
```

Materialization is deliberately library-first. The mapping/resolver behavior stays in
CATSS-TF; downstream integrations such as Agora should call the released API rather than
reimplement CATSS semantics.


## Special notation semantics

CATSS special notation is decoded into query-native `catss_sem_*` Text-Fabric features rather than requiring researchers to parse raw sigla or provenance sidecars. Context-bearing notation has corresponding `*_payload` features, and unknown notation fails validation instead of falling into a generic bucket. See [docs/special-notation.md](docs/special-notation.md) for semantic families, Sirach-specific scope, and query examples.
