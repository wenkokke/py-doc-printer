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
    is_buffering: bool = dataclasses.field(default=False, init=False, repr=False)
    line_width: int = dataclasses.field(default=0, init=False, repr=False)
    on_emit: list[OnEmit] = dataclasses.field(
        default_factory=list, init=False, repr=False
    )

    def emit(self, token: Token) -> Token:
        if self.is_buffering:
            return token
        else:
            if token is Line:
                self.line_width = 0
            else:
                self.line_width += len(token)
            for cb in self.on_emit:
                token = cb(token)
            return token

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
        yield from row_buffer.render(on_emit=self.emit)
        yield self.emit(Line)

    @render_simple.register
    def _(self, doc: Table) -> TokenStream:
        table_buffer = self.buffer_table(doc)
        yield from table_buffer.render(on_emit=self.emit)

    @render_simple.register
    def _(self, doc: Nest) -> TokenStream:
        first_line: bool = True
        has_content: bool = False
        line_indent: int = 0
        for token in self.buffer(doc.doc):
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
                            if doc.overlap and doc.indent > self.line_width:
                                yield from map(
                                    self.emit,
                                    itertools.repeat(
                                        Space,
                                        line_indent + doc.indent - self.line_width,
                                    ),
                                )
                        else:
                            yield from map(
                                self.emit,
                                itertools.repeat(Space, line_indent + doc.indent),
                            )
                        yield self.emit(token)

    @render_simple.register
    def _(self, doc: Map) -> TokenStream:
        for token in self.render(doc.doc):
            yield from doc.function(token)

    ###########################################################################
    # Buffering
    ###########################################################################

    @contextlib.contextmanager
    def buffering(self) -> collections.abc.Iterator[None]:
        self.is_buffering = True
        try:
            yield None
        finally:
            self.is_buffering = False

    def buffer(self, doc: Doc) -> TokenStream:
        with self.buffering():
            yield from self.render(doc)

    def buffer_row(self, row: Row) -> RowBuffer:
        row_buffer = RowBuffer(
            hsep=row.info.hsep, min_col_widths=row.info.min_col_widths
        )
        for cell in row.cells:
            cell_buffer = CellBuffer(hpad=row.info.hpad)
            cell_buffer.extend(self.buffer(cell))
            row_buffer.append(cell_buffer)
        row_buffer.update()
        return row_buffer

    def buffer_table(self, table: Table) -> TableBuffer:
        table_buffer = TableBuffer()
        table_buffer.extend(self.buffer_row(row) for row in table.rows)
        table_buffer.update()
        return table_buffer
