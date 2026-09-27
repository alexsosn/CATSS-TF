# Research — issue #50 MT-column `---` apparent minus

## Scope

Issue #50 was discovered by the complete-CATSS gate for the standalone canonical corpus.
The first blocking row after the known Genesis 6:19 source typo is:

```
Gen 8:8
--- =;L/R)T <8.8>    TOU= I)DEI=N
```

The current parser correctly produces zero MT lexical elements and two Greek lexical
elements, but it has no typed semantic for the MT-column-A `---` marker. Technique-v1
therefore rejects the alignment as an unexplained Hebrew-empty / Greek-nonempty group.

This research determines whether `---` is another spelling of LXX-plus or a different
CATSS judgment, and what representation preserves that distinction.

## Documentary and parser evidence

### CATSS column model

The CATSS parallel format treats Hebrew column A as the formal MT side of the
alignment. Optional Hebrew column B contains selected reconstructed/retroverted Hebrew
readings presumed behind the Greek. The current CATSS-TF parser already preserves this
split and classifies column-B prefixes independently.

Cody Kingham's reconstruction of the CATSS 1986/1991 documentation records two
different Hebrew-side alignment sigla in `regex_patterns.py`:

- `--+`: “In column A of the Hebrew: element added in the Greek”;
- `---`: “apparent minus in the MT over against the Greek”.

The distinction matters: the first is explicit evidence for an LXX addition versus MT;
the second says that the MT appears to lack material represented in Greek, often with a
column-B retroversion describing a presumed Hebrew counterpart.

The same source separately treats Greek-column `---` as a missing Greek counterpart,
i.e. the ordinary LXX-minus case. Position therefore changes the semantic direction.

### Independent current parser behavior

`curran-gehring/catss` recognizes `--+` in the Hebrew column as LXX-plus and
Greek-column `---` as LXX-minus. It does not currently model Hebrew-column `---` as
a separate typed fact. That omission cannot justify treating the marker as `--+`.

### Existing CATSS-TF vocabulary

CATSS-TF already has the documented semantic identity
`Ap- -> apparent_minus` in `notation.py`. The projection schema therefore already
knows how to create `catss_sem_apparent_minus*` features when an annotation of that
kind exists. Reusing this identity avoids introducing a second name for the same CATSS
concept.

CATSS-TF also already distinguishes:
- explicit LXX-plus (`is_lxx_plus`, `catss_lxx_plus`, technique
  `addition_vs_mt`);
- explicit LXX-minus (`is_lxx_minus`, `catss_lxx_minus`, technique
  `omission_vs_mt`);
- empty-side transposition carriers, which are admissible without being relabeled as
  additions/omissions.

The apparent-MT-minus case should follow the same conservative rule: make the explicit
source evidence admissible while keeping `addition_vs_mt=False`.

## Projection consequences

For LXX projection, the Greek words exist and can carry
`catss_sem_apparent_minus` with source scope `mt_a`.

For BHSA projection, there is no MT word corresponding to the apparent-minus group.
The existing precedent for explicit LXX-plus is a verse-level anchor on the BHSA parent
warp. A distinct apparent-MT-minus anchor is therefore the faithful query-native
representation on the MT projection; it must not reuse the LXX-plus anchor kind.

The standalone canonical corpus can preserve the alignment slot plus its typed
annotation directly.

## Questions for complete-snapshot audit

Before freezing behavior, scan all 46 current CATSS parallel files and report:

1. every Hebrew-empty / Greek-nonempty alignment grouped by first MT-column-A marker;
2. count and representative references for MT-column-A `---`;
3. whether all such rows are lexically empty on MT after parsing;
4. whether variants such as ditto markers, `{x}`, column-B retroversions or
   transposition markers materially alter the category;
5. any other zero-MT/nonempty-Greek marker class not already explained by `--+`,
   transposition, known source repair, or apparent minus.

Do not broaden the parser until this audit is complete.
