# Changelog

All notable CATSS-TF software changes are recorded here.

## Unreleased (main source, not the published v0.1.0 wheel)

### Fixed

- Prevent the standalone canonical Text-Fabric materializer from replacing an
  empty output directory created by a concurrent process between validation
  and publishing. Promotion now uses the atomic, fail-closed,
  `tf-build` no-clobber publication primitive. Existing destination
  symlinks (including dangling links) are rejected. No source text,
  alignment semantics, TF data or TSV provenance format changes.
- Delegate Agora host-created empty staging directory preflight to the
  published `tf-build` helper while keeping CATSS-specific source, symlink
  and source/output overlap checks.

### Dependency

- Source and future wheel installs pin the published `tf-build v0.1.0rc1`
  wheel by SHA256. Its `text-fabric>=13.1,<14` dependency means a core
  install now includes Text-Fabric; this is a runtime installation change.
  The existing public CATSS-TF v0.1.0 wheel is unchanged.


## 0.1.0 — 2026-09-26

Initial standalone release.

### Added

- user-invoked CATSS parallel-data acquisition from the upstream CCAT host;
- source fingerprinting and fail-closed CATSS parser/validation;
- canonical CATSS alignment IR with provenance, column-B retroversions, Ketiv/Qere,
  plus/minus, transposition, strategy sigla, and Greek reference handling;
- exact BHSA 2021 / v1.8.1 resolver and `catss-bhsa` materializer;
- exact CenterBLC/LXX 1935 / v1.0.1 resolver and `catss-lxx` materializer;
- query-native scalar Text-Fabric schema with no new nodes or warp replacement;
- normalized TSV provenance/diagnostic sidecars;
- cross-projection consistency checks;
- deterministic translation-technique v1 features;
- standard Text-Fabric browser integration through the native BHSA/LXX apps;
- Python 3.11–3.13 CI with strict mypy, Ruff, pytest, and wheel smoke testing.

### Data boundary

CATSS-TF v0.1.0 distributes software only. It does not redistribute CATSS, BHSA,
CenterBLC/LXX, or generated Text-Fabric modules.
