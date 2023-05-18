import itertools
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, List, Optional, Tuple

from .doc import Line, Token, TokenStream

TokenBuffer = List[Token]


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
    def min_width(self, min_width: int) -> None:
        self.width = max(min_width, self.width)
        self._min_width = min_width

    def __post_init__(self, **rest: Any) -> None:
        assert self.hpad is not Line

    def append(self, token: Token) -> None:
        self.min_width += len(token)
        self.buffer.append(token)

    def extend(self, tokens: Iterable[Token]) -> None:
        for token in tokens:
            self.append(token)

    def render(self, *, padding: bool = True) -> TokenStream:
        yield from self.buffer
        if padding:
            yield from self.padding()

    def padding(self) -> TokenStream:
        yield from itertools.repeat(self.hpad, self.width - self.min_width)

    def __iter__(self) -> TokenStream:
        return iter(self.buffer)


@dataclass
class RowBuffer(Iterable[CellBuffer]):
    hsep: Token
    min_col_widths: Tuple[Optional[int], ...]
    min_n_cols: int = field(default=0, init=False)
    buffer: List[CellBuffer] = field(default_factory=list, init=False)

    def __post_init__(self, **rest: Any) -> None:
        assert self.hsep is not Line

    def append(self, cell: CellBuffer) -> None:
        self.min_n_cols += 1
        self.buffer.append(cell)

    def extend(self, cells: Iterable[CellBuffer]) -> None:
        for cell in cells:
            self.append(cell)

    def render(self) -> TokenStream:
        for j, cell in enumerate(self):
            if j < len(self.buffer) - 1:
                yield from cell.render(padding=True)
                yield self.hsep
            else:
                yield from cell.render(padding=False)

    def update(self) -> None:
        for j in range(0, self.min_n_cols):
            try:
                min_col_widths_j: Optional[int] = self.min_col_widths[j]
                assert min_col_widths_j is not None
                self.buffer[j].width = min_col_widths_j
            except IndexError:
                pass

    def append_min_col_widths(self, min_col_widths: Tuple[Optional[int], ...]) -> None:
        self.min_n_cols = max(self.min_n_cols, len(min_col_widths))
        self.min_col_widths = tuple(
            max(w1 or 0, w2 or 0)
            for (w1, w2) in itertools.zip_longest(self.min_col_widths, min_col_widths)
        )

    def __iter__(self) -> Iterator[CellBuffer]:
        return iter(self.buffer)


@dataclass
class TableBuffer:
    n_cols: int = field(default=0, init=False)
    n_rows: int = field(default=0, init=False)
    buffer: List[RowBuffer] = field(default_factory=list, init=False)
    col_widths: Tuple[int, ...] = field(default_factory=tuple, init=False)

    def append(self, row: RowBuffer) -> None:
        self.n_cols = max(self.n_cols, row.min_n_cols)
        self.n_rows += 1
        self.buffer.append(row)
        self.append_min_col_widths(tuple(cell.min_width for cell in row))
        self.append_min_col_widths(row.min_col_widths)

    def extend(self, rows: Iterable[RowBuffer]) -> None:
        for row in rows:
            self.append(row)

    def render(self) -> TokenStream:
        for row in self:
            yield from row.render()
            yield Line

    def update(self) -> None:
        for i in range(0, self.n_rows):
            self.buffer[i].append_min_col_widths(self.col_widths)
            self.buffer[i].update()

    def append_min_col_widths(self, min_col_widths: Tuple[Optional[int], ...]) -> None:
        if not self.col_widths:
            self.col_widths = tuple(w or 0 for w in min_col_widths)
        else:
            self.col_widths = tuple(
                max(w1 or 0, w2 or 0)
                for (w1, w2) in itertools.zip_longest(self.col_widths, min_col_widths)
            )

    def __iter__(self) -> Iterator[RowBuffer]:
        return iter(self.buffer)
