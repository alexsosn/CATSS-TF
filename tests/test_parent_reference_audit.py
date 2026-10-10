"""Pinned-parent existence is not proof of CATSS Greek lexical alignment."""

import dataclasses

import pytest

from catss_tf.lxx_resolver import LxxSpan, LxxWord
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
from catss_tf.parent_reference_audit import audit_lxx_parent_span_availability
from catss_tf.parser import parse_parallel_text


def _probe() -> LxxParentProbe:
    return LxxParentProbe(
        repository=LXX_REPOSITORY,
        version=LXX_VERSION,
        release_tag=LXX_RELEASE_TAG,
        release_commit=LXX_RELEASE_COMMIT,
        slot_type=LXX_SLOT_TYPE,
        max_slot=LXX_MAX_SLOT,
        max_node=LXX_MAX_NODE,
        section_types=LXX_SECTION_TYPES,
        node_counts=LXX_NODE_COUNTS,
        feature_names=LXX_REQUIRED_FEATURES,
    )


def _span(
    book: str,
    chapter: int,
    verse: int,
    subverse: str | None = None,
) -> LxxSpan:
    return LxxSpan(
        node=850001,
        book=book,
        chapter=chapter,
        verse=verse,
        subverse=subverse,
        words=(LxxWord(node=1, word="λόγος", subverse=subverse or "", orig_order="1"),),
    )


class Provider:
    def __init__(self, spans: tuple[LxxSpan, ...], probe: LxxParentProbe | None = None):
        self.parent_probe = _probe() if probe is None else probe
        self.spans = {(x.book, x.chapter, x.verse, x.subverse): x for x in spans}
        self.requests: list[tuple[str, int, int, str | None]] = []

    def get_span(
        self, book: str, chapter: int, verse: int, subverse: str | None = None
    ) -> LxxSpan | None:
        key = (book, chapter, verse, subverse)
        self.requests.append(key)
        return self.spans.get(key)


def test_parent_span_existence_is_not_claimed_as_greek_textual_mapping() -> None:
    docs = (
        parse_parallel_text(
            "Gen 1:1\nHB\tLOGOS [2] [99]\n",
            source_name="01.Genesis.par",
        ),
        parse_parallel_text(
            "JoshB 9:2\nHB\tLOGOS [9:2a]\n",
            source_name="06.JoshB.par",
        ),
        parse_parallel_text(
            "Neh 1:1\nHB\tLOGOS [2]\n",
            source_name="19.Neh.par",
        ),
        parse_parallel_text(
            "JoshA 1:1\nHB\tLOGOS [2]\n",
            source_name="07.JoshA.par",
        ),
        parse_parallel_text(
            "Gen 1:1\nHB\tLOGOS [2]\n",
            source_name="99.Unknown.par",
        ),
    )
    provider = Provider(
        (
            _span("Gen", 1, 2),
            _span("Josh", 9, 2),  # unlabeled verse is NOT Greek 9:2a
            _span("2Esdr", 11, 2),  # inherited Neh chapter maps to 2Esdr chapter 11
        )
    )
    audit = audit_lxx_parent_span_availability(docs, provider)
    assert audit.source_files == 5
    assert audit.scalar_references == 6
    assert audit.parent_span_present == 2
    assert audit.parent_span_missing == 2
    assert audit.unsupported_source == 1
    assert audit.unknown_source == 1
    assert audit.subverse_suffixes == 1
    assert audit.subverse_present == 0
    assert audit.subverse_missing == 1
    assert audit.subverse_unprofiled == 0
    assert ("2Esdr", 11, 2, None) in provider.requests
    assert ("Josh", 9, 2, "a") in provider.requests
    assert ("Josh", 9, 2, None) not in provider.requests
    assert len(provider.requests) == 4  # unsupported and unknown fail closed


def test_parent_fingerprint_mismatch_fails_before_any_lookup() -> None:
    doc = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    provider = Provider(
        (_span("Gen", 1, 2),), dataclasses.replace(_probe(), release_commit="wrong")
    )
    with pytest.raises(ValueError, match="parent"):
        audit_lxx_parent_span_availability((doc,), provider)
    assert provider.requests == []


def test_parent_aliasing_subverse_must_fail_closed() -> None:
    class AliasProvider(Provider):
        def get_span(
            self, book: str, chapter: int, verse: int, subverse: str | None = None
        ) -> LxxSpan | None:
            self.requests.append((book, chapter, verse, subverse))
            return _span(book, chapter, verse, subverse=None)

    doc = parse_parallel_text(
        "JoshB 9:2\nHB\tLOGOS [9:2a]\n",
        source_name="06.JoshB.par",
    )
    with pytest.raises(ValueError, match="span"):
        audit_lxx_parent_span_availability((doc,), AliasProvider(()))


@pytest.mark.parametrize(
    ("requested_subverse", "word_subverse"),
    [("a", "b"), (None, "a")],
)
def test_parent_span_word_subverse_labels_must_match_claimed_span(
    requested_subverse: str | None,
    word_subverse: str,
) -> None:
    """The span's correct section key does not make mislabeled words valid."""
    ref = "[9:2a]" if requested_subverse == "a" else "[9:2]"
    doc = parse_parallel_text(
        f"JoshB 9:2\nHB\tLOGOS {ref}\n",
        source_name="06.JoshB.par",
    )
    span = dataclasses.replace(
        _span("Josh", 9, 2, requested_subverse),
        words=(LxxWord(node=1, word="λόγος", subverse=word_subverse, orig_order="1"),),
    )
    with pytest.raises(ValueError, match="word subverse"):
        audit_lxx_parent_span_availability((doc,), Provider((span,)))
