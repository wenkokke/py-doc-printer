import collections.abc
import contextlib
import dataclasses
import enum
import functools
import itertools

from .abc import *
from .doc import *
from .table import *


class SimpleLayout(enum.IntEnum):
    ShortestLines = 0  # Always pick the first alternative
    LongestLines = -1  # Always pick the last alternative


@dataclasses.dataclass
class SimpleDocRenderer(DocRenderer):
    simple_layout: SimpleLayout = SimpleLayout.ShortestLines

    def render(self, doc: Doc) -> TokenStream:
        yield from self.render_simple(doc)

    @functools.singledispatchmethod
    def render_simple(self, doc: Doc) -> TokenStream:
        raise TypeError(type(doc))

    @render_simple.register
    def _(self, doc: Text) -> TokenStream:
        yield self.emit(doc)

    @render_simple.register
    def _(self, doc: Alt) -> TokenStream:
        if doc.alts:
            yield from self.render(doc.alts[int(self.simple_layout)])
        else:
            return RenderError(doc)

    @render_simple.register
    def _(self, doc: Cat) -> TokenStream:
        yield from self.render_stream(doc.docs)

    @render_simple.register
    def _(self, doc: Row) -> TokenStream:
        row_buffer = self.buffer_row(doc)
        yield from map(self.emit, row_buffer.render())
        yield self.emit(Line)

    @render_simple.register
    def _(self, doc: Table) -> TokenStream:
        table_buffer = self.buffer_table(doc)
        yield from map(self.emit, table_buffer.render())

    @render_simple.register
    def _(self, doc: Nest) -> TokenStream:
        first_line: bool = True
        has_content: bool = False
        line_indent: int = 0
        buffer = self.buffer_stream(self.render(doc.doc))
        for token in buffer:
            if token is Line:
                first_line = False
                has_content = False
                line_indent = 0
                yield self.emit(Line)
            else:
                if has_content:
                    yield self.emit(token)
                else:
                    if token is Space:
                        line_indent += 1
                    else:
                        has_content = True
                        if first_line:
                            if doc.overlap and doc.indent > self.column:
                                yield from self.padding(
                                    line_indent + doc.indent - self.column
                                )
                        else:
                            yield from self.padding(line_indent + doc.indent)
                        yield self.emit(token)

    @render_simple.register
    def _(self, doc: Edit) -> TokenStream:
        buffer = self.buffer_stream(doc.function(self.render(doc.doc)))
        yield from map(self.emit, buffer)

    ###########################################################################
    # Padding
    ###########################################################################

    def padding(self, amount: int) -> TokenStream:
        yield from map(self.emit, itertools.repeat(Space, amount))

    ###########################################################################
    # Emitting Tokens & Tracking Position
    ###########################################################################

    on_emit: list[OnEmit] = dataclasses.field(default_factory=list)

    line: int = dataclasses.field(default=0, init=False)
    column: int = dataclasses.field(default=0, init=False)

    def emit(self, token: Token) -> Token:
        # Invoke all callbacks
        for cb in self.on_emit:
            token = cb(token)
        # Update position
        if token is Line:
            self.line += 1
            self.column = 0
        else:
            self.column += len(token)
        return token

    ###########################################################################
    # Buffering
    ###########################################################################

    position_stack: list[tuple[int, int]] = dataclasses.field(
        default_factory=list, init=False
    )

    @contextlib.contextmanager
    def buffering(self) -> collections.abc.Iterator[None]:
        self.position_stack.append((self.line, self.column))
        try:
            yield None
        finally:
            line, column = self.position_stack.pop()
            self.line = line
            self.column = column

    @property
    def is_buffering(self) -> bool:
        return bool(self.position_stack)

    def buffer_line(self, token_stream: TokenStream) -> tuple[TokenBuffer, TokenStream]:
        token_buffer: TokenBuffer = []
        with self.buffering():
            for token in token_stream:
                token_buffer.append(token)
                if token is Line:
                    break
        return (token_buffer, token_stream)

    def buffer_stream(self, token_stream: TokenStream) -> TokenBuffer:
        with self.buffering():
            token_buffer = list(token_stream)
        return token_buffer

    def buffer_row(self, row: Row) -> RowBuffer:
        row_buffer = RowBuffer(row.info.hsep, row.info.min_col_widths)
        for cell in row.cells:
            cell_buffer = CellBuffer(hpad=row.info.hpad)
            cell_buffer.extend(self.buffer_stream(self.render(cell)))
            row_buffer.append(cell_buffer)
        row_buffer.update()
        return row_buffer

    def buffer_table(self, table: Table) -> TableBuffer:
        table_buffer = TableBuffer()
        table_buffer.extend(self.buffer_row(row) for row in table.rows)
        table_buffer.update()
        return table_buffer
