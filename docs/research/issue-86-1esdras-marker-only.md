# Research — #86 1 Esdras 4:28 marker-only mixed notation

## Trigger / observation

The complete 46-file CCAT audit isolated one exceptional record:

- file: `17.1Esdras.par`; reference: `1Esdr 4:28`;
- original logical source row: `--- ''\t--+`;
- zero lexical MT elements and zero lexical Greek elements;
- typed MT-side `apparent_minus` from initial `---`;
- neighboring preceding lines in the same verse include repeated Hebrew-side
  `--+ ''` markers associated with Greek-added elements.

This is **not** one of the 61 valid lexical Greek apparent-minus rows, nor
Jonah 4:3's one-Hebrew/two-Greek mixed alignment.

## Independent prior parser and documentation evidence

At pinned `codykingham/CATSS_parsers@dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35`:

1. `parallel_readme.md`, “Categories of Markup”, explicitly calls
   `''` a **columner** that modifies a **whole column of words**. That
   describes its scope class but does **not** define a ditto/copy operation
   or the exact `--- '' → --+` combination.
   https://github.com/codykingham/CATSS_parsers/blob/dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35/parallel_readme.md
2. `regex_patterns.py`, `common_tc`, treats `--+ ''` as a
   Hebrew-column-A marker for an “element added in the Greek” and `--- ''`
   as an “apparent minus in the MT over against the Greek”. Its regex
   matches both notations generally, without demonstrating that `--+`
   written in the **Greek** column of this zero/zero row is a Greek
   addition or a subtraction.
   https://github.com/codykingham/CATSS_parsers/blob/dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35/regex_patterns.py

Both are third-party reconstructions of a difficult and partly corrupted
export. The same prior README points to the original 1991 CCAT
`00.ReadReParallel.txt` and Tov's 1986 CATSS vol. 2 as primary sources,
but their precise treatment of this exceptional combination has **not yet
been verified**.

## Negative evidence / decision R86-1

No Greek lexical surface or unique existing parent word is provided by
`--- ''\t--+`. Treating Greek `--+` as a positive Greek word token,
or using this record to create a word-node membership in LXX, would
fabricate a correspondence. Collapsing `--- ''` into an ordinary
`(0,n)` apparent-minus group would silently break cardinality.

Keep the exact source spelling, position, annotations, physical provenance,
and alignment ID. The current conservative zero/zero `TechniqueError`
remains correct **pending further evidence**, not a definitive semantics.

## Research still needed

Inspect consecutive real 1Esdr 4:28 records, where the apparent-plus
and apparent-minus markers switch, with their original physical lines.
Check the primary 1991 CCAT sigla and the underlying Rahlfs 1 Esdras
Greek text for the alignment boundary. Compare `''` on similarly
structured neighboring `--+` groups before deciding whether this is
a column-wide scope-closure, a malformed source row, or a valid
nonlexical annotation carrier. A future implementation must be exact
identity-based and must not admit generic zero/zero apparent-minus.

Do not change parser/resolver/technique semantics without completing
this research, a committed RED regression demonstrating the intended
behavior, full 46-file audit and independent review.
