# CATSS-TF

CATSS-TF is a materializer-only project for projecting the CATSS Hebrew–Greek parallel alignment onto existing Text-Fabric corpora.

The intended outputs are two locally generated TF modules:

- `catss-bhsa` — CATSS alignment annotations attached to nodes of ETCBC/BHSA;
- `catss-lxx` — the same canonical CATSS alignments projected onto nodes of CenterBLC/LXX.

This repository does **not** distribute BHSA, LXX, raw CATSS data, or generated TF corpora. It contains software, mapping profiles, tests, and documentation needed to build modules from data acquired by the user under the relevant upstream terms.

## Status

Bootstrap/research stage. No materializer is implemented yet.

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
