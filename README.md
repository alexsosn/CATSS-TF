# CATSS-TF

CATSS-TF is a materializer-only project for projecting the CATSS Hebrew–Greek parallel alignment onto existing Text-Fabric corpora.

The intended outputs are two locally generated TF modules:

- `catss-bhsa` — CATSS alignment annotations attached to nodes of ETCBC/BHSA;
- `catss-lxx` — the same canonical CATSS alignments projected onto nodes of CenterBLC/LXX.

This repository does **not** distribute BHSA, LXX, raw CATSS data, or generated TF corpora. It contains software, mapping profiles, tests, and documentation needed to build modules from data acquired by the user under the relevant upstream terms.

## Status

Both CATSS projections, cross-projection consistency checks, and the initial
translation-technique layer are implemented. v0.1 release preparation is in progress.

Read:

1. [research.md](research.md)
2. [design.md](design.md)
3. [plan.md](plan.md)
4. [AGENTS.md](AGENTS.md)
5. [docs/agentic-dev-loop.md](docs/agentic-dev-loop.md)

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

See [docs/browser.md](docs/browser.md) for exact pinned commands and search examples.\n\n## Special notation semantics\n\nCATSS special notation is decoded into query-native `catss_sem_*` Text-Fabric features rather than requiring researchers to parse raw sigla or provenance sidecars. Context-bearing notation has corresponding `*_payload` features, and unknown notation fails validation instead of falling into a generic bucket. See [docs/special-notation.md](docs/special-notation.md) for the semantic families, Sirach-specific profile, scope rules, and query examples.
