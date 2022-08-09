import abc
import collections.abc
import dataclasses
import itertools
import re
import typing

import dataclasses_json
import more_itertools

DocLike = typing.Union[None, str, "Doc", collections.abc.Iterable["DocLike"]]  # type: ignore

DocClassWithUnpack = type[collections.abc.Iterable["Doc"]]


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class WidthHint:
    width: int = 0
    end_of_line: bool = False

    def __add__(self, other: typing.Union[int, "Doc", "WidthHint"]) -> "WidthHint":
        if self.end_of_line:
            return self
        else:
            if isinstance(other, int):
                other = WidthHint(other)
            if isinstance(other, Doc):
                other = other.width_hint()
            return WidthHint(self.width + other.width, other.end_of_line)

    def __radd__(self, other: typing.Union[int, "Doc", "WidthHint"]) -> "WidthHint":
        if isinstance(other, int):
            other = WidthHint(other)
        if isinstance(other, Doc):
            other = other.width_hint()
        return other.__add__(self)


class Doc(abc.ABC):
    def then(self, other: DocLike) -> "Doc":
        """
        Compose two documents.
        """
        return cat(self, other)

    def join(self, *others: DocLike) -> "Doc":
        """
        Compose a series of documents separated by this document.
        """
        # NOTE: The first 'splat' is to ensure that a separator is
        #       inserted between any two of the top-level Docs, but
        #       not between Docs which are already part of a Cat.
        #       The call to cat then flattens out any existing Cats,
        #       without inserting additional separators.
        return cat(more_itertools.intersperse(self, splat(others)))

    @abc.abstractmethod
    def width_hint(self) -> WidthHint:
        """
        Return an estimate of the width of the first line, when this document is rendered.
        """

    def __truediv__(self, other: DocLike) -> "Doc":
        """
        Compose two documents.
        """
        return self.then(other)

    def __rtruediv__(self, other: DocLike) -> "Doc":
        """
        Compose two documents.
        """
        return cat(other).then(self)

    def __floordiv__(self, other: DocLike) -> "Doc":
        """
        Compose two documents, separated by a space.
        """
        other = cat(other)
        if self is Empty or self is Space:
            return other
        if other is Empty or other is Space:
            return self
        if isinstance(self, Cat) and self.docs[-1] is Space:
            return self.then(other)
        if isinstance(other, Cat) and other.docs[0] is Space:
            return self.then(other)
        return self.then(Space).then(other)

    def __rfloordiv__(self, other: DocLike) -> "Doc":
        """
        Compose two documents, separated by a space.
        """
        return cat(other).__floordiv__(self)

    def __or__(self, other: DocLike) -> "Doc":
        """
        Combine two documents as alternatives.
        """
        return alt(self, other)

    def __ror__(self, other: DocLike) -> "Doc":
        """
        Combine two documents as alternatives.
        """
        return alt(other, self)


################################################################################
# Text and Tokens
################################################################################


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Text(Doc):
    """
    A single line of text.
    """

    text: str

    RE_ONE_WHITESPACE: typing.ClassVar[re.Pattern[str]] = re.compile(r"\s")
    RE_ANY_WHITESPACE: typing.ClassVar[re.Pattern[str]] = re.compile(r"\s+")

    @classmethod
    def words(cls, text: str, *, collapse_whitespace: bool = False) -> Doc:
        if collapse_whitespace:
            pattern = cls.RE_ANY_WHITESPACE
        else:
            pattern = cls.RE_ONE_WHITESPACE
        return Space.join(map(Text, pattern.split(text)))

    @classmethod
    def lines(cls, text: str, *, collapse_whitespace: bool = False) -> Doc:
        return Line.join(
            cls.words(line, collapse_whitespace=collapse_whitespace)
            for line in text.splitlines()
        )

    @classmethod
    def intern(cls, name: str, text: str) -> "Text":
        if not hasattr(cls, name):
            instance = super().__new__(Text)
            object.__setattr__(instance, "text", text)
            setattr(cls, name, instance)
        return getattr(cls, name)

    @classmethod
    def intern_Empty(cls) -> "Text":
        return cls.intern("Empty", "")

    def is_Empty(self) -> bool:
        return self is self.__class__.intern_Empty()

    @classmethod
    def intern_Space(cls) -> "Text":
        return cls.intern("Space", " ")

    def is_Space(self) -> bool:
        return self is self.__class__.intern_Space()

    @classmethod
    def intern_Line(cls) -> "Text":
        return cls.intern("Line", "\n")

    def is_Line(self) -> bool:
        return self is self.__class__.intern_Line()

    def __new__(cls, text: str) -> "Text":
        if text == cls.intern_Empty().text:
            return cls.intern_Empty()
        if text == cls.intern_Space().text:
            return cls.intern_Space()
        if text == cls.intern_Line().text:
            return cls.intern_Line()
        instance = super().__new__(Text)
        object.__setattr__(instance, "text", text)
        return instance

    def __init__(self, text: str) -> None:
        # Invariant: The text does not contain whitespace.
        assert (
            re.match(r"\S+", self.text)
            or self.is_Empty()
            or self.is_Space()
            or self.is_Line()
        )

    def __repr__(self) -> str:
        if self.is_Empty():
            return "Empty"
        if self.is_Space():
            return "Space"
        if self.is_Line():
            return "Line"
        return f"Text(text={self.text})"

    def width_hint(self) -> WidthHint:
        if self is Line:
            return WidthHint(width=0, end_of_line=True)
        else:
            return WidthHint(width=len(self), end_of_line=False)

    def __len__(self) -> int:
        return len(self.text)


Empty = Text.intern_Empty()

Space = Text.intern_Space()

Line = Text.intern_Line()


Token = Text
TokenStream = collections.abc.Iterator[Token]


################################################################################
# Concatenation
################################################################################


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Cat(Doc, collections.abc.Iterable[Doc]):
    """
    Concatenated documents.
    """

    docs: tuple[Doc, ...]

    def __post_init__(self, **rest) -> None:
        # Invariant: None of docs is an instance of Cat.
        assert all(
            not isinstance(doc, Cat) for doc in self.docs
        ), f"Cat contains Cat:\n{repr(self)}"
        # Invariant: None of docs is Empty.
        assert all(
            doc is not Empty for doc in self.docs
        ), f"Cat contains Empty:\n{repr(self)}"

    def __iter__(self) -> collections.abc.Iterator[Doc]:
        return iter(self.docs)

    def width_hint(self) -> WidthHint:
        width_hint = WidthHint()
        for doc in self.docs:
            width_hint = width_hint + doc
            if width_hint.end_of_line:
                return width_hint  # short-circuit
        return width_hint


def splat(
    doclike: DocLike,
    unpack: typing.Union[DocClassWithUnpack, tuple[DocClassWithUnpack, ...]] = (),
) -> collections.abc.Iterator["Doc"]:
    """
    Iterate over the elements any document-like object.
    """
    if not isinstance(unpack, tuple):
        unpack = (unpack,)
    if doclike is None:
        pass
    elif isinstance(doclike, str):
        yield from splat(Text.lines(doclike), unpack=unpack)
    elif isinstance(doclike, Doc):
        if isinstance(doclike, unpack):
            yield from typing.cast(collections.abc.Iterable["Doc"], doclike)
        else:
            yield doclike
    else:
        for smaller_doclike in doclike:
            yield from splat(smaller_doclike, unpack=unpack)


def cat(*doclike: DocLike) -> "Doc":
    """
    Concatenate a series of documents or document-like objects.

    NOTE: `cat` and `Empty` form a monoid, where `Empty` acts as a unit for `cat`
    """
    docs = tuple(filter(bool, splat(doclike, unpack=Cat)))
    if len(docs) == 0:
        return Empty
    if len(docs) == 1:
        return docs[0]
    return Cat(docs)


def parens(*doclike: DocLike) -> Doc:
    return cat("(", doclike, ")")


def brackets(*doclike: DocLike) -> Doc:
    return cat("[", doclike, "]")


def braces(*doclike: DocLike) -> Doc:
    return cat("{", doclike, "}")


def angles(*doclike: DocLike) -> Doc:
    return cat("<", doclike, ">")


################################################################################
# Alternatives
################################################################################


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Alt(Doc, collections.abc.Iterable[Doc]):
    """
    Alternatives for the document layout.
    """

    # Assume: The alternatives are listed in increasing order of width.
    alts: tuple[Doc, ...]

    @classmethod
    def intern(cls, name: str, alts: tuple[Doc, ...]) -> "Alt":
        if not hasattr(cls, name):
            instance = super().__new__(Alt)
            object.__setattr__(instance, "alts", alts)
            setattr(cls, name, instance)
        return getattr(cls, name)

    @classmethod
    def intern_Fail(cls) -> "Alt":
        return cls.intern("Fail", ())

    def is_Fail(self) -> bool:
        return self is self.__class__.intern_Fail()

    @classmethod
    def intern_SoftLine(cls) -> "Alt":
        return cls.intern("SoftLine", (Line, Empty))

    def is_SoftLine(self) -> bool:
        return self is self.__class__.intern_SoftLine()

    def __new__(cls, alts: tuple[Doc, ...]) -> "Alt":
        if alts == cls.intern_Fail().alts:
            return cls.intern_Fail()
        if alts == cls.intern_SoftLine().alts:
            return cls.intern_SoftLine()
        instance = super().__new__(Alt)
        object.__setattr__(instance, "alts", alts)
        return instance

    def __init__(self, alts: tuple[Doc, ...]):
        # Invariant: None of alts is an instance of Alt.
        assert all(
            not isinstance(doc, Alt) for doc in self.alts
        ), f"Alt contains Alt:\n{repr(self)}"

    def __repr__(self) -> str:
        if self.is_Fail():
            return "Fail"
        if self.is_SoftLine():
            return "SoftLine"
        return f"Alt(alts={self.alts})"

    def __iter__(self) -> collections.abc.Iterator[Doc]:
        return iter(self.alts)

    def width_hint(self) -> WidthHint:
        if self.alts:  # i.e., self is not Fail
            return self.alts[0].width_hint()
        else:
            return WidthHint()  # TODO: raise exception?


Fail = Alt.intern_Fail()


SoftLine = Alt.intern_SoftLine()


def alt(*doclike: DocLike) -> Doc:
    alts = tuple(splat(doclike, unpack=Alt))
    if len(alts) == 1:
        return alts[0]
    else:
        return Alt(alts)


################################################################################
# Nesting and Indentation
################################################################################


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Nest(Doc):
    """
    Indented documents.
    """

    indent: int
    doc: Doc
    overlap: bool = False

    def __post_init__(self, **rest) -> None:
        # Invariant: The doc is not Nest
        assert not isinstance(self.doc, Nest), f"Nest contains Nest:\n{repr(self)}"
        # Invariant: The doc is not Empty
        assert self.doc is not Empty, f"Nest contains Empty:\n{repr(self)}"
        # Invariant: The indent is greater than zero.
        assert self.indent > 0, f"Nest has negative or zero indent:\n{repr(self)}"

    def width_hint(self) -> WidthHint:
        if self.overlap:
            # TODO: use the current column to decide more accurately?
            return self.indent + self.doc.width_hint()
        else:
            return self.doc.width_hint()


def nest(indent: int, *doclike: DocLike, overlap: bool = False) -> Doc:
    doc = cat(doclike)
    if doc is Empty:
        return Empty
    if isinstance(doc, Nest):
        indent += doc.indent
        doc = doc.doc
    if indent < 1:
        return doc
    return Nest(indent=indent, doc=doc, overlap=overlap)


################################################################################
# Automatic Escaping: TokenStream editing via Edit
################################################################################


def _escape_single(token_stream: TokenStream) -> TokenStream:
    return map(escape_single, token_stream)


def _escape_single_and_unescape_double(token_stream: TokenStream) -> TokenStream:
    return _escape_single(map(unescape_single, token_stream))


def _escape_double(token_stream: TokenStream) -> TokenStream:
    return map(escape_double, token_stream)


def _escape_double_and_unescape_single(token_stream: TokenStream) -> TokenStream:
    return _escape_double(map(unescape_single, token_stream))


def _smart_quote(token_stream: TokenStream) -> TokenStream:
    single: int = 0
    double: int = 0
    buffer: list[Token] = []
    for token in token_stream:
        single += token.text.count("'")
        double += token.text.count('"')
        buffer.append(token)
    if single < double:
        yield Text("'")
        yield from _escape_single_and_unescape_double(iter(buffer))
        yield Text("'")
    else:
        yield Text('"')
        yield from _escape_double_and_unescape_single(iter(buffer))
        yield Text('"')


def _inline(token_stream: TokenStream) -> TokenStream:
    return filter(lambda token: token is not Line, token_stream)


def _encode_edit_function(
    function: collections.abc.Callable[[TokenStream], TokenStream]
) -> str:
    if function is _escape_single:
        return "_escape_single"
    if function is _escape_single_and_unescape_double:
        return "_escape_single_and_unescape_double"
    if function is _escape_double:
        return "_escape_double"
    if function is _escape_double_and_unescape_single:
        return "_escape_double_and_unescape_single"
    if function is _smart_quote:
        return "_smart_quote"
    if function is _inline:
        return "_inline"
    raise ValueError(f"Unknown edit function '{repr(function)}'")


def _decode_edit_function(
    function_name: str,
) -> collections.abc.Callable[[TokenStream], TokenStream]:
    if function_name is "_escape_single":
        return _escape_single
    if function_name is "_escape_single_and_unescape_double":
        return _escape_single_and_unescape_double
    if function_name is "_escape_double":
        return _escape_double
    if function_name is "_escape_double_and_unescape_single":
        return _escape_double_and_unescape_single
    if function_name is "_smart_quote":
        return _smart_quote
    if function_name is "_inline":
        return _inline
    raise ValueError(f"Unknown edit function '{function_name}'")


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Edit(Doc):
    function: collections.abc.Callable[[TokenStream], TokenStream] = dataclasses.field(
        metadata=dataclasses_json.config(
            encoder=_encode_edit_function,
            decoder=_decode_edit_function,
        )
    )
    doc: Doc

    def width_hint(self) -> WidthHint:
        # NOTE: function should not significantly alter the width
        return self.doc.width_hint()


ESCAPED_SINGLE_QUOTE: re.Pattern[str] = re.compile(r"\\'")


def unescape_single(token: Token) -> Token:
    return Text(ESCAPED_SINGLE_QUOTE.sub(r"'", token.text))


UNESCAPED_SINGLE_QUOTE: re.Pattern[str] = re.compile(r"(?<!\\)'")


def escape_single(token: Token) -> Token:
    return Text(UNESCAPED_SINGLE_QUOTE.sub(r"\'", token.text))


ESCAPED_DOUBLE_QUOTE: re.Pattern[str] = re.compile(r'\\"')


def unescape_double(token: Token) -> Token:
    return Text(ESCAPED_DOUBLE_QUOTE.sub(r'"', token.text))


UNESCAPED_DOUBLE_QUOTE: re.Pattern[str] = re.compile(r'(?<!\\)"')


def escape_double(token: Token) -> Token:
    return Text(UNESCAPED_DOUBLE_QUOTE.sub(r"\"", token.text))


def single_quote(
    *doclike: DocLike, auto_escape: bool = True, auto_unescape: bool = True
) -> Doc:
    doc = cat(doclike)
    if auto_escape:
        if auto_unescape:
            doc = Edit(_escape_single_and_unescape_double, doc)
        else:
            doc = Edit(_escape_single, doc)
    return cat("'", doc, "'")


def double_quote(
    *doclike: DocLike, auto_escape: bool = True, auto_unescape: bool = True
) -> Doc:
    doc = cat(doclike)
    if auto_escape:
        if auto_unescape:
            doc = Edit(_escape_double_and_unescape_single, doc)
        else:
            doc = Edit(_escape_double, doc)
    return cat('"', doc, '"')


def smart_quote(*doclike: DocLike) -> Doc:
    return Edit(_smart_quote, cat(doclike))


################################################################################
# Inline: Removing Lines
################################################################################


def inline(doc: Doc) -> Doc:
    return Edit(_inline, doc=doc)


################################################################################
# Alignment: Rows and Tables
################################################################################


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class RowInfo:
    table_type: typing.Optional[str]
    hpad: Text
    hsep: Text
    min_col_widths: tuple[typing.Optional[int], ...]


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Row(Doc, collections.abc.Iterable[Doc]):
    cells: tuple[Doc, ...]
    info: RowInfo

    def __post_init__(self, **rest) -> None:
        # Invariant: None of cells is an instance of Row.
        assert all(
            not isinstance(cell, Row) for cell in self.cells
        ), f"Row contains Row:\n{repr(self)}"
        # Invariant: The hpad text has width 1.
        assert self.info.hpad.text is not Empty, f"Row hpad is Empty:\n'{repr(self)}'"
        assert (
            len(self.info.hpad.text) == 1
        ), f"Row hpad is more than one character:\n'{repr(self)}'"

    def __iter__(self) -> collections.abc.Iterator[Doc]:
        return iter(self.cells)

    def width_hint(self) -> WidthHint:
        width_hint = WidthHint()
        for cell in more_itertools.intersperse(self.info.hsep, self.cells):
            # NOTE: sum the length of the first line of each cell
            width_hint = width_hint + cell.width_hint().width
        # NOTE: rows always end the line
        return WidthHint(width_hint.width, True)


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Table(Doc, collections.abc.Iterable[Row]):
    rows: tuple[Row, ...]

    def __post_init__(self, **rest) -> None:
        # Invariant: All of rows are an instance of Table.
        assert all(
            isinstance(row, Row) for row in self.rows
        ), f"Table contains non-Row:\n{repr(self)}"

    def __iter__(self) -> collections.abc.Iterator[Row]:
        return iter(self.rows)

    def width_hint(self) -> WidthHint:
        if self.rows:
            # NOTE: only process the first row
            return self.rows[0].width_hint()
        else:
            return WidthHint()


def row(
    *doclike: DocLike,
    table_type: typing.Optional[str] = None,
    hpad: typing.Union[str, Text] = Space,
    hsep: typing.Union[str, Text] = Space,
    min_col_widths: tuple[typing.Optional[int], ...] = (),
) -> Doc:
    # Ensure padding and separators are Text
    if isinstance(hpad, str):
        hpad = Text(hpad)
    if isinstance(hsep, str):
        hsep = Text(hsep)
    info = RowInfo(
        table_type=table_type, hpad=hpad, hsep=hsep, min_col_widths=min_col_widths
    )
    # Ensure Row settings are preserved
    cells: list[Doc] = []
    for cell_or_row in splat(doclike):
        if isinstance(cell_or_row, Row):
            assert cell_or_row.info == info
            cells.extend(cell_or_row.cells)
        else:
            cells.append(cell_or_row)
    return Row(tuple(cells), info=info)


def table(rows: collections.abc.Iterator[Row]) -> Doc:
    return Table(tuple(rows))


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class RowCandidate:
    doc: Doc

    @property
    def row(self) -> typing.Optional[Row]:
        if isinstance(self.doc, Row):
            return self.doc
        if isinstance(self.doc, Alt):
            for alt in self.doc.alts:
                if isinstance(alt, Row):
                    return alt
        return None

    @property
    def table_type(self) -> typing.Union[bool, str]:
        if self.row:
            return self.row.info.table_type or True
        return False

    def __iter__(self) -> collections.abc.Iterator[typing.Union[Doc, Row, None]]:
        yield self.doc
        yield self.row


def create_table(*doclike: DocLike) -> typing.Optional[Table]:
    buffer: list[Row] = []
    previous_doc_was_row: bool = False
    row_candidates = map(RowCandidate, splat(doclike))
    for row_candidate in row_candidates:
        if row_candidate.row:
            buffer.append(row_candidate.row)
            previous_doc_was_row = True
        elif row_candidate.doc is Line and previous_doc_was_row:
            previous_doc_was_row = False
        else:
            return None
    # NOTE: only return tables with >=2 rows
    if len(buffer) < 2:
        return None
    else:
        return Table(tuple(iter(buffer)))


def create_tables(
    docs: collections.abc.Iterator[Doc], *, separator: Text = Line
) -> collections.abc.Iterator[Doc]:
    row_candidates = map(RowCandidate, docs)
    table_candidates = itertools.groupby(row_candidates, key=lambda rc: rc.table_type)
    for _, group in table_candidates:
        subdocs, subrows = zip(*group)
        table = create_table(subrows)
        if table:
            yield alt(separator.join(subdocs), table)
        else:
            yield from subdocs
