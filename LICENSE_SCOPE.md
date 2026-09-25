# License scope

## CATSS-TF software

Code and original project documentation in this repository are licensed under the MIT License in `LICENSE`.

## Data are separate

The MIT license does not relicense any upstream data.

CATSS source files, CATSS alignment annotations, and CATSS-derived databases are governed by the terms of their data owners/distributors. The public CATSS ecosystem describes non-commercial restrictions and a separate user agreement for CATSS data.

BHSA is an independently distributed parent corpus with its own data license. CenterBLC/LXX is an independently distributed parent corpus and also has its own provenance and licensing terms.

CATSS-TF intentionally does not commit or release:

- raw CATSS files;
- prebuilt CATSS SQLite databases;
- generated CATSS alignment modules;
- BHSA corpus data;
- LXX corpus data.

Materializers operate on data acquired separately by the user. A locally generated module is a derivative artifact whose redistribution rights depend on all applicable upstream terms; this repository's MIT license alone is not permission to redistribute that generated data.

## Dependency code

Third-party software dependencies retain their own licenses. Copying source from an upstream parser is not permitted merely because CATSS-TF is MIT; any reused source must be compatible with MIT distribution and attributed as required.
