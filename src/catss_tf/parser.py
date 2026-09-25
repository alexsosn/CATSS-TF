"""Parser for CATSS parallel-alignment source files."""

import dataclasses
import hashlib
import pathlib
import re
import typing

_VERSE_HEADER = re.compile(r"^\s*([0-9A-Za-z][0-9A-Za-z/]*)\s+(?:(\d+):)?(\d+)\s*$")
_COLUMN_SPACES = re.compile(r"\s{2,}")
_BRACE_BLOCK = re.compile(r"\{[^{}]*\}")
_ANGLE_NOTE = re.compile(r"<[^<>]*>")
_SQUARE_REFERENCE = re.compile(r"\[[^\[\]]*\]")
_SINGLE_CARET = re.compile(r"(?<!\^)\^(?!\^)")
_SINGLE_STAR = re.compile(r"(?<!\*)\*(?!\*)")
_CONTINUATION_TOKEN = re.compile(r"(?:(?<=^)|(?<=\s))#(?=\s|$)")


@dataclasses.dataclass(frozen=True, slots=True)
class Annotation:
    """One source annotation preserved from a CATSS alignment cell."""

    side: typing.Literal["mt", "lxx"]
    kind: str
    raw: str


@dataclasses.dataclass(frozen=True, slots=True)
class ParseDiagnostic:
    """A source structure that could not be interpreted without uncertainty."""

    code: str
    line_no: int
    raw_line: str
    message: str


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
    mt_tokens: tuple[str, ...]
    lxx_tokens: tuple[str, ...]
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
        source_path.read_text(encoding="utf-8", errors="replace"),
        source_name=source_path.name,
    )


def parse_parallel_text(text: str, *, source_name: str) -> ParallelDocument:
    """Parse CATSS parallel text without mapping it to a parent corpus."""

    canonical_source = pathlib.Path(source_name).name
    diagnostics: list[ParseDiagnostic] = []
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
    is_lxx_plus = mt_col_a.lstrip().startswith("--+")
    is_lxx_minus = lxx_raw.lstrip().startswith("---")

    annotations = tuple(
        [
            *_extract_annotations("mt", mt_raw),
            *_extract_annotations("lxx", lxx_raw),
        ]
    )

    mt_probe = _BRACE_BLOCK.sub(" ", mt_col_a)
    is_qere = "**" in mt_probe
    is_ketiv = _SINGLE_STAR.search(mt_probe) is not None

    joined_raw = f"{mt_raw}\t{lxx_raw}"
    no_braces = _BRACE_BLOCK.sub(" ", joined_raw)
    is_transposition_stylistic = any(
        annotation.kind == "transposition_stylistic" for annotation in annotations
    )
    is_transposition_remote = (
        "^^^" in joined_raw
        or any(annotation.kind == "transposition_remote" for annotation in annotations)
    )
    is_transposition_local = "~" in no_braces or _SINGLE_CARET.search(no_braces) is not None

    mt_tokens = () if is_lxx_plus else _lexical_candidates(mt_col_a, side="mt")
    lxx_tokens = () if is_lxx_minus else _lexical_candidates(lxx_raw, side="lxx")

    source_lines = tuple(row.line_no for row in physical_rows)
    raw_lines = tuple(row.raw for row in physical_rows)
    alignment_id = _alignment_id(
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
            mt_tokens=mt_tokens,
            lxx_tokens=lxx_tokens,
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
    side: typing.Literal["mt", "lxx"], cell: str
) -> list[Annotation]:
    annotations: list[Annotation] = []
    for match in _BRACE_BLOCK.finditer(cell):
        raw = match.group(0)
        annotations.append(Annotation(side=side, kind=_brace_kind(raw), raw=raw))
    for match in _ANGLE_NOTE.finditer(cell):
        annotations.append(Annotation(side=side, kind="note", raw=match.group(0)))
    if side == "mt":
        for match in _MT_DOT_SIGLUM.finditer(cell):
            raw = match.group(1)
            annotations.append(Annotation(side=side, kind=_mt_dot_kind(raw), raw=raw))
    if side == "lxx":
        for match in _SQUARE_REFERENCE.finditer(cell):
            annotations.append(
                Annotation(side=side, kind="verse_reference", raw=match.group(0))
            )
    return annotations


def _mt_dot_kind(raw: str) -> str:
    return {
        ".m": "metathesis",
        ".s": "word_separation",
        ".j": "word_join",
        ".w": "word_division",
        ".z": "abbreviation",
    }.get(raw, "mt_strategy_siglum")


def _brace_kind(raw: str) -> str:
    exact = {
        "{d}": "doublet",
        "{t}": "transliteration",
        "{x}": "apparent_plus_minus",
        "{*}": "greek_agrees_ketiv",
        "{**}": "greek_agrees_qere",
    }
    if raw in exact:
        return exact[raw]
    if raw.startswith("{..^") or raw.startswith("{..p^"):
        return "transposition_stylistic"
    if raw.startswith("{..."):
        return "transposition_remote"
    return "unknown"


def _lexical_candidates(cell: str, *, side: typing.Literal["mt", "lxx"]) -> tuple[str, ...]:
    text = _BRACE_BLOCK.sub(lambda match: _brace_payload(match.group(0)), cell)
    text = _ANGLE_NOTE.sub(" ", text)
    text = _SQUARE_REFERENCE.sub(" ", text)
    text = _CONTINUATION_TOKEN.sub(" ", text)

    tokens: list[str] = []
    for raw_token in text.split():
        token = raw_token
        if token in {"--+", "---", "''", "^", "^^^", "~"}:
            continue
        if side == "mt" and token.startswith("."):
            continue
        token = token.lstrip("*") if side == "mt" else token
        token = token.strip()
        if token:
            tokens.append(token)
    return tuple(tokens)


def _brace_payload(raw: str) -> str:
    inner = raw[1:-1]
    if inner.startswith("..p^"):
        return inner[4:]
    if inner.startswith("..^"):
        return inner[3:]
    if inner.startswith("..."):
        return inner[3:]
    return " "


def _cell_has_trailing_hash(cell: str) -> bool:
    return bool(re.search(r"(?:^|\s)#\s*$", cell))


def _cell_has_leading_hash(cell: str) -> bool:
    return bool(re.match(r"^#(?:\s|$)", cell))


def _alignment_id(
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
