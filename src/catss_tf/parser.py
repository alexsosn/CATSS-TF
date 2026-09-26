"""Parser for CATSS parallel-alignment source files."""

import dataclasses
import hashlib
import pathlib
import re
import typing

from catss_tf.notation import notation_spec

_VERSE_HEADER = re.compile(r"^\s*([0-9A-Za-z][0-9A-Za-z/]*)\s+(?:(\d+):)?(\d+)\s*$")
_COLUMN_SPACES = re.compile(r"\s{2,}")
_BRACE_BLOCK = re.compile(r"\{[^{}]*\}")
_ANGLE_NOTE = re.compile(r"<[^<>]*>")
_SQUARE_GROUP = re.compile(r"\[\[?[^\[\]]*\]\]?")
_GREEK_REFERENCE_VALUE = re.compile(r"^(?:(\d+):)?(\d+)([A-Za-z]?)$")
_SINGLE_CARET = re.compile(r"(?<!\^)\^(?!\^)")
_CONTINUATION_TOKEN = re.compile(r"(?:(?<=^)|(?<=\s))#(?=\s|$)")
_MT_DOT_SIGLUM = re.compile(r"(?<!\S)(\.[^\s]+)")
_DOUBT_MARKER = re.compile(r"\?+")
_LXX_PLUS_MARKERS = frozenset({"--+", "-+", "---+"})
_LXX_MINUS_MARKERS = frozenset({"---", "--", "----"})


@dataclasses.dataclass(frozen=True, slots=True)
class Annotation:
    """One source annotation preserved from a CATSS alignment cell."""

    side: typing.Literal["mt_a", "mt_b", "lxx"]
    kind: str
    raw: str
    family: str | None = None
    contextual: bool = False
    payload: str | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class ParseDiagnostic:
    """A source structure that could not be interpreted without uncertainty."""

    code: str
    line_no: int
    raw_line: str
    message: str


@dataclasses.dataclass(frozen=True, slots=True)
class GreekReference:
    """Structured CATSS Greek-side reference override."""

    chapter: int | None
    verse: int
    subverse: str | None
    raw: str


@dataclasses.dataclass(frozen=True, slots=True)
class MtReading:
    """One MT word position with optional Ketiv/Qere alternatives."""

    primary: str
    ketiv: str | None
    qere: str | None
    doubtful: bool
    aramaic_section: bool


@dataclasses.dataclass(frozen=True, slots=True)
class AlignmentRecord:
    """Canonical representation of one logical CATSS alignment row."""

    alignment_id: str
    source_lines: tuple[int, ...]
    raw_lines: tuple[str, ...]
    mt_raw: str
    lxx_raw: str
    mt_col_a: str
    mt_col_b: str | None
    retroversion_kind: str | None
    mt_readings: tuple[MtReading, ...]
    mt_tokens: tuple[str, ...]
    mt_ketiv_tokens: tuple[str, ...]
    mt_qere_tokens: tuple[str, ...]
    lxx_tokens: tuple[str, ...]
    lxx_references: tuple[GreekReference, ...]
    mt_count: int
    lxx_count: int
    is_lxx_plus: bool
    is_lxx_minus: bool
    has_retroversion: bool
    is_ketiv: bool
    is_qere: bool
    is_transposition_local: bool
    is_transposition_remote: bool
    is_transposition_stylistic: bool
    annotations: tuple[Annotation, ...]
    column_split: bool


@dataclasses.dataclass(frozen=True, slots=True)
class VerseRecord:
    """CATSS alignments under one source verse header."""

    book: str
    chapter: int
    verse: int
    header_raw: str
    header_line_no: int
    alignments: tuple[AlignmentRecord, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class ParallelDocument:
    """Parsed representation of one CATSS parallel file."""

    source_name: str
    data_line_numbers: tuple[int, ...]
    verses: tuple[VerseRecord, ...]
    diagnostics: tuple[ParseDiagnostic, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class _PhysicalRow:
    line_no: int
    raw: str
    mt: str
    lxx: str
    column_split: bool

    @property
    def continues(self) -> bool:
        return _cell_has_trailing_hash(self.mt) or _cell_has_trailing_hash(self.lxx)

    @property
    def starts_with_continuation(self) -> bool:
        return _cell_has_leading_hash(self.mt) or _cell_has_leading_hash(self.lxx)


@dataclasses.dataclass(slots=True)
class _VerseBuilder:
    book: str
    chapter: int
    verse: int
    header_raw: str
    header_line_no: int
    alignments: list[AlignmentRecord]


def parse_parallel_file(path: str | pathlib.Path) -> ParallelDocument:
    """Parse a local CATSS parallel file."""

    source_path = pathlib.Path(path)
    return parse_parallel_text(
        source_path.read_text(encoding="utf-8"),
        source_name=source_path.name,
    )


def parse_parallel_text(text: str, *, source_name: str) -> ParallelDocument:
    """Parse CATSS parallel text without mapping it to a parent corpus."""

    canonical_source = pathlib.Path(source_name).name
    diagnostics: list[ParseDiagnostic] = []
    data_line_numbers: list[int] = []
    verses: list[VerseRecord] = []
    current: _VerseBuilder | None = None
    pending: list[_PhysicalRow] = []

    def flush_pending() -> None:
        nonlocal pending
        if not pending or current is None:
            pending = []
            return
        if pending[-1].continues:
            diagnostics.append(
                ParseDiagnostic(
                    code="malformed_continuation",
                    line_no=pending[-1].line_no,
                    raw_line=pending[-1].raw,
                    message="continuation marker is not followed by another data line",
                )
            )
        alignment, row_diagnostics = _build_alignment(
            source_name=canonical_source,
            verse=current,
            physical_rows=tuple(pending),
        )
        current.alignments.append(alignment)
        diagnostics.extend(row_diagnostics)
        pending = []

    def flush_verse() -> None:
        nonlocal current
        flush_pending()
        if current is None:
            return
        verses.append(
            VerseRecord(
                book=current.book,
                chapter=current.chapter,
                verse=current.verse,
                header_raw=current.header_raw,
                header_line_no=current.header_line_no,
                alignments=tuple(current.alignments),
            )
        )
        current = None

    for line_no, raw_with_end in enumerate(text.splitlines(), start=1):
        raw = raw_with_end.rstrip("\r")
        if not raw.strip():
            continue

        header = _VERSE_HEADER.match(raw)
        if header:
            flush_verse()
            current = _VerseBuilder(
                book=header.group(1),
                chapter=int(header.group(2)) if header.group(2) else 1,
                verse=int(header.group(3)),
                header_raw=raw,
                header_line_no=line_no,
                alignments=[],
            )
            continue

        data_line_numbers.append(line_no)

        if current is None:
            diagnostics.append(
                ParseDiagnostic(
                    code="orphan_line",
                    line_no=line_no,
                    raw_line=raw,
                    message="nonblank content occurred before the first verse header",
                )
            )
            continue

        physical = _parse_physical_row(raw, line_no)
        if pending:
            if pending[-1].continues:
                pending.append(physical)
                if not physical.continues:
                    flush_pending()
                continue
            flush_pending()

        if physical.starts_with_continuation:
            diagnostics.append(
                ParseDiagnostic(
                    code="malformed_continuation",
                    line_no=line_no,
                    raw_line=raw,
                    message="continuation line has no preceding continued row",
                )
            )

        pending = [physical]
        if not physical.continues:
            flush_pending()

    flush_verse()
    return ParallelDocument(
        source_name=canonical_source,
        data_line_numbers=tuple(data_line_numbers),
        verses=tuple(verses),
        diagnostics=tuple(diagnostics),
    )


def _parse_physical_row(raw: str, line_no: int) -> _PhysicalRow:
    if "\t" in raw:
        mt, lxx = raw.split("\t", 1)
        return _PhysicalRow(
            line_no=line_no,
            raw=raw,
            mt=mt.strip(),
            lxx=lxx.strip(),
            column_split=True,
        )

    parts = _COLUMN_SPACES.split(raw, maxsplit=1)
    if len(parts) == 2:
        return _PhysicalRow(
            line_no=line_no,
            raw=raw,
            mt=parts[0].strip(),
            lxx=parts[1].strip(),
            column_split=True,
        )

    return _PhysicalRow(
        line_no=line_no,
        raw=raw,
        mt=raw.strip(),
        lxx="",
        column_split=False,
    )


def _build_alignment(
    *,
    source_name: str,
    verse: _VerseBuilder,
    physical_rows: tuple[_PhysicalRow, ...],
) -> tuple[AlignmentRecord, tuple[ParseDiagnostic, ...]]:
    row_diagnostics: list[ParseDiagnostic] = []
    mt_raw = _join_continued_cells(row.mt for row in physical_rows)
    lxx_raw = _join_continued_cells(row.lxx for row in physical_rows)
    column_split = all(row.column_split for row in physical_rows)

    if not column_split:
        first_unsplit = next(row for row in physical_rows if not row.column_split)
        row_diagnostics.append(
            ParseDiagnostic(
                code="unsplit_row",
                line_no=first_unsplit.line_no,
                raw_line=first_unsplit.raw,
                message="logical row could not be confidently split into MT and LXX columns",
            )
        )

    mt_col_a, mt_col_b = _split_mt_columns(mt_raw)
    is_lxx_plus = _first_token(mt_col_a) in _LXX_PLUS_MARKERS
    is_lxx_minus = _first_token(lxx_raw) in _LXX_MINUS_MARKERS

    lxx_references, reference_diagnostics = _extract_greek_references(
        lxx_raw,
        line_no=physical_rows[0].line_no,
        raw_line=physical_rows[0].raw,
    )
    row_diagnostics.extend(reference_diagnostics)

    annotations = tuple(
        [
            *_extract_annotations("mt_a", mt_col_a, book=verse.book),
            *(
                _extract_annotations("mt_b", mt_col_b, book=verse.book)
                if mt_col_b is not None
                else []
            ),
            *_extract_annotations("lxx", lxx_raw, book=verse.book),
        ]
    )

    mt_readings = _mt_lexical_readings(mt_col_a)
    mt_tokens = tuple(reading.primary for reading in mt_readings)
    mt_ketiv_tokens = tuple(reading.ketiv for reading in mt_readings if reading.ketiv is not None)
    mt_qere_tokens = tuple(reading.qere for reading in mt_readings if reading.qere is not None)
    is_ketiv = bool(mt_ketiv_tokens)
    is_qere = bool(mt_qere_tokens)

    joined_raw = f"{mt_raw}\t{lxx_raw}"
    no_braces = _BRACE_BLOCK.sub(" ", joined_raw)
    is_transposition_stylistic = any(
        annotation.kind == "transposition_stylistic" for annotation in annotations
    )
    is_transposition_remote = "^^^" in joined_raw or any(
        annotation.kind == "transposition_remote" for annotation in annotations
    )
    is_transposition_local = "~" in no_braces or _SINGLE_CARET.search(no_braces) is not None

    retroversion_kind = _retroversion_kind(mt_col_b)
    if is_lxx_plus:
        mt_readings = ()
        mt_tokens = ()
        mt_ketiv_tokens = ()
        mt_qere_tokens = ()
    lxx_tokens = () if is_lxx_minus else _lxx_lexical_candidates(lxx_raw)

    source_lines = tuple(row.line_no for row in physical_rows)
    raw_lines = tuple(row.raw for row in physical_rows)
    alignment_id = alignment_id_for(
        source_name=source_name,
        header_raw=verse.header_raw,
        source_lines=source_lines,
        raw_lines=raw_lines,
    )

    return (
        AlignmentRecord(
            alignment_id=alignment_id,
            source_lines=source_lines,
            raw_lines=raw_lines,
            mt_raw=mt_raw,
            lxx_raw=lxx_raw,
            mt_col_a=mt_col_a,
            mt_col_b=mt_col_b,
            retroversion_kind=retroversion_kind,
            mt_readings=mt_readings,
            mt_tokens=mt_tokens,
            mt_ketiv_tokens=mt_ketiv_tokens,
            mt_qere_tokens=mt_qere_tokens,
            lxx_tokens=lxx_tokens,
            lxx_references=lxx_references,
            mt_count=len(mt_tokens),
            lxx_count=len(lxx_tokens),
            is_lxx_plus=is_lxx_plus,
            is_lxx_minus=is_lxx_minus,
            has_retroversion=mt_col_b is not None,
            is_ketiv=is_ketiv,
            is_qere=is_qere,
            is_transposition_local=is_transposition_local,
            is_transposition_remote=is_transposition_remote,
            is_transposition_stylistic=is_transposition_stylistic,
            annotations=annotations,
            column_split=column_split,
        ),
        tuple(row_diagnostics),
    )


def _split_mt_columns(mt_raw: str) -> tuple[str, str | None]:
    index = mt_raw.find("=")
    if index < 0:
        return mt_raw.strip(), None
    return mt_raw[:index].rstrip(), mt_raw[index + 1 :].strip()


def _join_continued_cells(cells: typing.Iterable[str]) -> str:
    parts: list[str] = []
    for cell in cells:
        cleaned = _CONTINUATION_TOKEN.sub(" ", cell)
        cleaned = " ".join(cleaned.split())
        if cleaned:
            parts.append(cleaned)
    return " ".join(parts)


def _extract_annotations(
    side: typing.Literal["mt_a", "mt_b", "lxx"], cell: str, *, book: str
) -> list[Annotation]:
    annotations: list[Annotation] = []
    double_brace_spans: set[tuple[int, int]] = set()
    if book == "Sir":
        for match in _SIRACH_DOUBLE_BRACE.finditer(cell):
            raw = match.group(0)
            double_brace_spans.add(match.span())
            spec = notation_spec("{{}}", book=book)
            if spec is not None:
                annotations.append(
                    Annotation(side=side, kind=spec.kind, raw=raw, family=spec.family)
                )

    for match in _BRACE_BLOCK.finditer(cell):
        if any(start <= match.start() and match.end() <= end for start, end in double_brace_spans):
            continue
        raw = match.group(0)
        if book == "Sir" and re.fullmatch(r"{(?:10|[1-9])\\??}", raw):
            witness = raw[1:-1].rstrip("?")
            annotations.append(
                Annotation(
                    side=side,
                    kind="sirach_lacuna_in_witness",
                    raw=raw,
                    family="sirach_manuscript",
                    payload=witness,
                )
            )
            continue
        if raw == "{!}":
            suffix_match = re.match(r"[a-z+\\-]*", cell[match.end() :])
            suffix = suffix_match.group(0) if suffix_match is not None else ""
            inf_abs_raw = raw + suffix
            annotations.append(
                Annotation(
                    side=side,
                    kind=_inf_abs_kind(suffix),
                    raw=inf_abs_raw,
                    family="infinitive_absolute",
                    payload=suffix or None,
                )
            )
            continue
        spec = notation_spec(raw, book=book)
        if spec is not None:
            annotations.append(
                Annotation(
                    side=side,
                    kind=spec.kind,
                    raw=raw,
                    family=spec.family,
                    contextual=spec.contextual,
                )
            )
        else:
            raw_kind = _brace_kind(raw)
            raw_semantics = {
                "distributive": ("distributive", "translation_technique", True),
                "preposition_added": ("preposition_added", "preposition", True),
                "transposition_remote": ("transposition_remote", "transposition", True),
                "transposition_stylistic": ("transposition_stylistic", "transposition", True),
                "repetition": ("repetition", "translation_technique", True),
            }.get(raw_kind)
            if raw_semantics is None:
                annotations.append(Annotation(side=side, kind=raw_kind, raw=raw))
            else:
                kind, family, contextual = raw_semantics
                payload = _annotation_brace_payload(raw, raw_kind)
                annotations.append(
                    Annotation(
                        side=side,
                        kind=kind,
                        raw=raw,
                        family=family,
                        contextual=contextual,
                        payload=payload,
                    )
                )
    for match in _ANGLE_NOTE.finditer(cell):
        raw = match.group(0)
        spec = notation_spec(raw, book=book)
        if spec is not None:
            annotations.append(
                Annotation(
                    side=side,
                    kind=spec.kind,
                    raw=raw,
                    family=spec.family,
                    contextual=spec.contextual,
                    payload=raw[1:-1] or None,
                )
            )
        else:
            annotations.append(
                Annotation(
                    side=side,
                    kind="source_note",
                    raw=raw,
                    family="reference",
                    contextual=True,
                    payload=raw[1:-1] or None,
                )
            )
    if side in {"mt_a", "mt_b"}:
        for match in _MT_DOT_SIGLUM.finditer(cell):
            raw = match.group(1)
            kind = _mt_dot_kind(raw)
            annotations.append(
                Annotation(
                    side=side,
                    kind=kind,
                    raw=raw,
                    family="segmentation" if kind != "letter_interchange" else "reconstruction",
                    payload=raw[1:] if kind == "letter_interchange" else None,
                )
            )
    if book == "Sir":
        for match in _SQUARE_GROUP.finditer(cell):
            raw = match.group(0)
            key = "[..]" if raw == "[..]" else "[]"
            spec = notation_spec(key, book=book)
            if spec is not None:
                annotations.append(
                    Annotation(
                        side=side,
                        kind=spec.kind,
                        raw=raw,
                        family=spec.family,
                        payload=raw.lstrip("[").rstrip("]") or None,
                    )
                )
        for match in re.finditer(r"(?<!\\S)(10|[1-9])(?=\\s|$)", cell):
            raw = match.group(1)
            spec = notation_spec(raw, book=book)
            if spec is not None:
                annotations.append(
                    Annotation(side=side, kind=spec.kind, raw=raw, family=spec.family)
                )
        for match in re.finditer(r">(?:10|[1-9])", cell):
            raw = match.group(0)
            spec = notation_spec(">", book=book)
            if spec is not None:
                annotations.append(
                    Annotation(
                        side=side,
                        kind=spec.kind,
                        raw=raw,
                        family=spec.family,
                        payload=raw[1:],
                    )
                )
        for match in re.finditer(r"(?<!\\*)\\*(?!\\*)", cell):
            spec = notation_spec("*", book=book)
            if spec is not None:
                annotations.append(
                    Annotation(side=side, kind=spec.kind, raw="*", family=spec.family)
                )

    if side == "lxx":
        for match in _DOUBT_MARKER.finditer(cell):
            annotations.append(Annotation(side=side, kind="doubt", raw=match.group(0)))
        for match in _SQUARE_GROUP.finditer(cell):
            raw = match.group(0)
            inner = raw.lstrip("[").rstrip("]")
            if any(character.isdigit() for character in inner):
                if _GREEK_REFERENCE_VALUE.fullmatch(inner) is not None:
                    annotations.append(
                        Annotation(
                            side=side,
                            kind="verse_reference",
                            raw=raw,
                            family="reference",
                            contextual=True,
                            payload=inner,
                        )
                    )
                else:
                    annotations.append(
                        Annotation(
                            side=side,
                            kind="contextual_reference",
                            raw=raw,
                            family="reference",
                            contextual=True,
                            payload=inner,
                        )
                    )
            elif notation_spec(raw, book=book) is None:
                annotations.append(Annotation(side=side, kind="unknown", raw=raw))
    return annotations


def _extract_greek_references(
    cell: str,
    *,
    line_no: int,
    raw_line: str,
) -> tuple[tuple[GreekReference, ...], tuple[ParseDiagnostic, ...]]:
    references: list[GreekReference] = []
    diagnostics: list[ParseDiagnostic] = []
    for match in _SQUARE_GROUP.finditer(cell):
        raw = match.group(0)
        inner = raw.lstrip("[").rstrip("]")
        if not any(character.isdigit() for character in inner):
            continue
        parsed = _GREEK_REFERENCE_VALUE.fullmatch(inner)
        if parsed is None:
            continue
        suffix = parsed.group(3) or None
        references.append(
            GreekReference(
                chapter=int(parsed.group(1)) if parsed.group(1) is not None else None,
                verse=int(parsed.group(2)),
                subverse=suffix.lower() if suffix is not None else None,
                raw=raw,
            )
        )
    return tuple(references), tuple(diagnostics)


def _retroversion_kind(mt_col_b: str | None) -> str | None:
    if mt_col_b is None:
        return None
    probe = mt_col_b.lstrip("?")
    if probe.startswith(":"):
        return "proper_noun"
    if probe.startswith(";"):
        return "context"
    if probe.startswith("%vap"):
        return "active_to_passive"
    if probe.startswith("%vpa"):
        return "passive_to_active"
    if probe.startswith("%p-"):
        return "preposition_omission"
    if probe.startswith("%p+"):
        return "preposition_addition"
    if probe.startswith("%p"):
        return "preposition_difference"
    if probe.startswith("@"):
        return "etymological"
    if probe.startswith("vs"):
        return "vocalization_shin_sin"
    if probe.startswith("v"):
        return "vocalization"
    if probe.startswith("r"):
        return "incomplete"
    if probe.startswith("+"):
        return "number_difference"
    return "plain"


def _mt_dot_kind(raw: str) -> str:
    return {
        ".m": "metathesis",
        ".s": "word_separation",
        ".j": "word_join",
        ".w": "word_division",
        ".z": "abbreviation",
    }.get(
        raw,
        "letter_interchange" if raw.startswith(".") and len(raw) > 2 else "mt_strategy_siglum",
    )


def _inf_abs_kind(suffix: str) -> str:
    return {
        "": "infinitive_absolute",
        "+": "inf_abs_without_mt_inf_abs",
        "-": "inf_abs_rendered_finite_verb",
        "--": "inf_abs_and_main_verb_omitted",
        "ad": "inf_abs_rendered_finite_verb_adverb",
        "aj": "inf_abs_rendered_finite_verb_adjective",
        "n": "inf_abs_rendered_finite_verb_noun",
        "na": "inf_abs_rendered_accusative_noun",
        "nad": "inf_abs_rendered_different_accusative_noun",
        "nd": "inf_abs_rendered_dative_noun",
        "nd+": "inf_abs_dative_without_mt_inf_abs",
        "ndd": "inf_abs_rendered_different_dative_noun",
        "p": "inf_abs_rendered_participle",
        "p+": "inf_abs_participle_without_mt_inf_abs",
        "pc": "inf_abs_rendered_participle_compositum",
        "pd": "inf_abs_rendered_different_verb_participle",
        "v": "inf_abs_rendered_verb",
    }.get(suffix, "unknown")


def _annotation_brace_payload(raw: str, kind: str) -> str | None:
    """Extract contextual payload from encoded CATSS brace families."""

    prefixes = {
        "distributive": "{..d",
        "preposition_added": "{..p",
        "transposition_remote": "{...",
        "transposition_stylistic": "{..^",
        "repetition": "{..r",
        "greek_correction": "{c",
        "greek_edition_difference": "{g",
    }
    prefix = prefixes.get(kind)
    if prefix is None or not raw.startswith(prefix) or not raw.endswith("}"):
        return None
    payload = raw[len(prefix) : -1]
    return payload or None


def _brace_kind(raw: str) -> str:
    exact = {
        "{d}": "doublet",
        "{t}": "transliteration",
        "{x}": "apparent_plus_minus",
        "{*}": "greek_agrees_ketiv",
        "{**}": "greek_agrees_qere",
        "{p}": "greek_preverb",
        "{s}": "comparative_superlative",
        "{---%}": "asterisked_passage",
    }
    if raw in exact:
        return exact[raw]
    if raw.startswith("{..^") or raw.startswith("{..p^"):
        return "transposition_stylistic"
    if raw.startswith("{..."):
        return "transposition_remote"
    if raw.startswith("{..p"):
        return "preposition_added"
    if raw.startswith("{..d"):
        return "distributive"
    if raw.startswith("{..r"):
        return "repetition"
    if raw.startswith("{c"):
        return "greek_correction"
    if raw.startswith("{g"):
        return "greek_edition_difference"
    return "unknown"


def _mt_lexical_readings(cell: str) -> tuple[MtReading, ...]:
    text = _prepare_lexical_text(cell)
    readings: list[MtReading] = []
    pending_aramaic = False
    pending_doubt = False

    for raw_token in text.split():
        if _is_alignment_marker(raw_token) or raw_token.startswith("."):
            continue

        token = raw_token
        if token == ",,a":
            if readings:
                previous = readings[-1]
                readings[-1] = dataclasses.replace(previous, aramaic_section=True)
            else:
                pending_aramaic = True
            continue

        aramaic_here = ",,a" in token
        token = token.replace(",,a", "")

        if token and set(token) == {"?"}:
            pending_doubt = True
            pending_aramaic = pending_aramaic or aramaic_here
            continue

        doubtful = pending_doubt or token.startswith("?") or token.endswith("?")
        pending_doubt = False
        token = token.strip("?")
        if not token:
            pending_aramaic = pending_aramaic or aramaic_here
            continue

        aramaic_here = aramaic_here or pending_aramaic

        if token.startswith("**") and len(token) > 2:
            qere = token[2:]
            if readings and readings[-1].ketiv is not None and readings[-1].qere is None:
                previous = readings[-1]
                readings[-1] = dataclasses.replace(
                    previous,
                    qere=qere,
                    doubtful=previous.doubtful or doubtful,
                    aramaic_section=previous.aramaic_section or aramaic_here,
                )
            else:
                readings.append(
                    MtReading(
                        primary=qere,
                        ketiv=None,
                        qere=qere,
                        doubtful=doubtful,
                        aramaic_section=aramaic_here,
                    )
                )
            pending_aramaic = False
            continue

        if token.startswith("*") and len(token) > 1:
            ketiv = token[1:]
            readings.append(
                MtReading(
                    primary=ketiv,
                    ketiv=ketiv,
                    qere=None,
                    doubtful=doubtful,
                    aramaic_section=aramaic_here,
                )
            )
            pending_aramaic = False
            continue

        readings.append(
            MtReading(
                primary=token,
                ketiv=None,
                qere=None,
                doubtful=doubtful,
                aramaic_section=aramaic_here,
            )
        )
        pending_aramaic = False

    return tuple(readings)


def _lxx_lexical_candidates(cell: str) -> tuple[str, ...]:
    text = _prepare_lexical_text(cell).replace("?", "")
    return tuple(
        token for token in text.split() if token != "+" and not _is_alignment_marker(token)
    )


def _prepare_lexical_text(cell: str) -> str:
    text = _BRACE_BLOCK.sub(lambda match: _brace_payload(match.group(0)), cell)
    text = _ANGLE_NOTE.sub(" ", text)
    text = _SQUARE_GROUP.sub(lambda match: _square_payload(match.group(0)), text)
    return _CONTINUATION_TOKEN.sub(" ", text)


def _square_payload(raw: str) -> str:
    inner = raw.lstrip("[").rstrip("]")
    if any(character.isdigit() for character in inner):
        return " "
    return inner


def _first_token(cell: str) -> str:
    parts = cell.split(maxsplit=1)
    return parts[0] if parts else ""


def _is_alignment_marker(token: str) -> bool:
    return (
        token in _LXX_PLUS_MARKERS
        or token in _LXX_MINUS_MARKERS
        or token in {"''", "^", "^^^", "~"}
    )


def _brace_payload(raw: str) -> str:
    inner = raw[1:-1]
    if inner.startswith("..p^"):
        return inner[4:]
    if inner.startswith("..^"):
        return inner[3:]
    if inner.startswith("..."):
        return inner[3:]
    if inner.startswith("..p"):
        return inner[3:]
    if inner.startswith("..d"):
        return inner[3:]
    if inner.startswith("..r"):
        return inner[3:]
    if inner.startswith("c"):
        return inner[1:]
    if inner.startswith("g"):
        return inner[1:]
    return " "


def _cell_has_trailing_hash(cell: str) -> bool:
    tokens = cell.split()
    return len(tokens) >= 2 and tokens[-1] == "#" and any(token != "#" for token in tokens[:-1])


def _cell_has_leading_hash(cell: str) -> bool:
    return bool(re.match(r"^#(?:\s|$)", cell))


def alignment_id_for(
    *,
    source_name: str,
    header_raw: str,
    source_lines: tuple[int, ...],
    raw_lines: tuple[str, ...],
) -> str:
    payload = "\x1f".join(
        (
            source_name,
            header_raw,
            ",".join(str(line) for line in source_lines),
            "\x1e".join(raw_lines),
        )
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
    return f"catss:{source_name}:{digest}"
