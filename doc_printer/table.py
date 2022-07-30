from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from itertools import repeat, zip_longest
from typing import Optional, TypeAlias

from .abc import OnEmit
from .doc import Line, Token, TokenStream


TokenBuffer: TypeAlias = list[Token]


@dataclass
class CellBuffer(Iterable[Token]):

    hpad: Token
    width: int = 0
    buffer: TokenBuffer = field(default_factory=list, init=False)
    _min_width: int = field(default=0, init=False, repr=False)

    @property
    def min_width(self) -> int:
        return self._min_width

    @min_width.setter
    def min_width(self, min_width: int):
        self.width = max(min_width, self.width)
        self._min_width = min_width

    def __post_init__(self, **rest):
        assert self.hpad is not Line

    def append(self, token: Token):
        self.min_width += len(token)
        self.buffer.append(token)

    def extend(self, token_stream: TokenStream):
        for token in token_stream:
            self.append(token)

    def render(self, padding: bool = True) -> TokenStream:
        yield from self.buffer
        if padding:
            yield from self.padding()

    def padding(self) -> TokenStream:
        yield from repeat(self.hpad, self.width - self.min_width)

    def __iter__(self) -> TokenStream:
        return iter(self.buffer)


@dataclass
class RowBuffer(Iterable[CellBuffer]):
    hsep: Token
    min_col_widths: tuple[Optional[int], ...]
    min_n_cols: int = field(default=0, init=False)
    buffer: list[CellBuffer] = field(default_factory=list, init=False)

    def __post_init__(self, **rest):
        assert self.hsep is not Line

    def append(self, cell: CellBuffer):
        self.min_n_cols += 1
        self.buffer.append(cell)

    def extend(self, cells: Iterable[CellBuffer]):
        for cell in cells:
            self.append(cell)

    def render(self, *, on_emit: OnEmit | None = None) -> TokenStream:
        if not on_emit:
            on_emit = lambda token: token
        for j, cell in enumerate(self):
            if j < len(self.buffer) - 1:
                yield from map(on_emit, cell.render(padding=True))
                yield on_emit(self.hsep)
            else:
                yield from map(on_emit, cell.render(padding=False))

    def __iter__(self) -> Iterator[CellBuffer]:
        return iter(self.buffer)


@dataclass
class TableBuffer:
    n_cols: int = field(default=0, init=False)
    n_rows: int = field(default=0, init=False)
    buffer: list[RowBuffer] = field(default_factory=list, init=False)
    col_widths: tuple[int, ...] = field(default_factory=tuple, init=False)

    def append(self, row: RowBuffer):
        self.n_cols = max(self.n_cols, row.min_n_cols)
        self.n_rows += 1
        self.buffer.append(row)
        self.append_min_col_widths(tuple(cell.min_width for cell in row))
        self.append_min_col_widths(row.min_col_widths)

    def extend(self, rows: Iterable[RowBuffer]):
        for row in rows:
            self.append(row)

    def render(self, *, on_emit: OnEmit | None = None) -> TokenStream:
        for row in self:
            yield from row.render(on_emit=on_emit)
            yield on_emit(Line) if on_emit else Line

    def update(self):
        for i in range(0, self.n_rows):
            for j in range(0, self.n_cols):
                col_width = self.col_widths[j]
                self.buffer[i].buffer[j].width = col_width

    def append_min_col_widths(self, min_col_widths: tuple[Optional[int], ...]):
        if not self.col_widths:
            self.col_widths = tuple(w or 0 for w in min_col_widths)
        else:
            self.col_widths = tuple(
                max(w1 or 0, w2 or 0)
                for (w1, w2) in zip_longest(self.col_widths, min_col_widths)
            )

    def __iter__(self) -> Iterator[RowBuffer]:
        return iter(self.buffer)
