# Changelog

All notable CATSS-TF software changes are recorded here.

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
