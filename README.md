# CATSS-TF

CATSS-TF is a materializer-only project for projecting the CATSS Hebrew–Greek parallel alignment onto existing Text-Fabric corpora.

The intended outputs are two locally generated TF modules:

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

Install with Text-Fabric integration:

```sh
pip install \\
  "catss-tf[tf] @ https://github.com/alexsosn/CATSS-TF/releases/download/v0.1.0/catss_tf-0.1.0-py3-none-any.whl"
```

Verify:

```sh
catss-tf --version
```

Read:

1. [docs/integration.md](docs/integration.md) — opt-in real-corpus materialization
2. [docs/browser.md](docs/browser.md) — standard Text-Fabric browser/search
3. [docs/case-studies/magic-terminology.md](docs/case-studies/magic-terminology.md) — worked Hebrew↔Greek lexical case study
4. [CHANGELOG.md](CHANGELOG.md)
5. [research.md](research.md)
6. [design.md](design.md)
7. [plan.md](plan.md)
8. [AGENTS.md](AGENTS.md)

## Architectural boundary

CATSS is the source of alignment semantics. BHSA and LXX remain the owners of their node identities and linguistic annotation.

A Text-Fabric module is a collection of additional features built around an existing warp. CATSS-TF therefore does not create an `alignment` node type in a module. Instead, both projections attach a shared stable `catss_alignment_id` and related CATSS features to existing parent nodes.

The materialization model is:

```text
CATSS source acquired by user
          |
          v
canonical CATSS alignment IR
       /                  \
      v                    v
resolve Hebrew          resolve Greek
to BHSA nodes           to LXX nodes
      |                    |
      v                    v
catss-bhsa             catss-lxx
TF module              TF module
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
    materialize_lxx,
)
```

Materialization is deliberately library-first. The mapping/resolver behavior stays in
CATSS-TF; downstream integrations such as Agora should call the released API rather than
reimplement CATSS semantics.
