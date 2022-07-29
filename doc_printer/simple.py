from functools import singledispatchmethod
from .doc import *
from .typing import *
from .abc import *
from .table import *

@dataclass
class SimpleDocRenderer(DocRenderer):
    is_buffering: bool = field(default=False, init=False, repr=False)
    line_width: int = field(default=0, init=False, repr=False)
    on_emit: list[OnEmit] = field(default_factory=list, init=False, repr=False)

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

    @overrides
    def render(self, doc: Doc) -> TokenStream:
        yield from self.render_simple(doc)

    @singledispatchmethod
    def render_simple(self, doc: Doc) -> TokenStream:
        raise TypeError(type(doc))

    @render_simple.register
    def _(self, doc: Text) -> TokenStream:
        yield self.emit(doc)

    @render_simple.register
    def _(self, doc: Alt) -> TokenStream:
        if doc.alts:
            yield from self.render(doc.alts[0])
        else:
            return RenderError(doc)

    @render_simple.register
    def _(self, doc: Cat) -> TokenStream:
        yield from self.render_stream(doc.docs)

    @render_simple.register
    def _(self, doc: Row) -> TokenStream:
        yield from self.buffer_row(doc).render(on_emit=self.emit)
        yield self.emit(Line)

    @render_simple.register
    def _(self, doc: Table) -> TokenStream:
        yield from self.buffer_table(doc).render(on_emit=self.emit)

    @render_simple.register
    def _(self, doc: Nest) -> TokenStream:
        has_content: bool = False
        line_indent: int = 0
        for token in self.render(doc.doc):
            if token is Line:
                has_content = False
                yield Line
            else:
                if has_content:
                    yield token
                else:
                    if token is Space:
                        line_indent += 1
                    else:
                        has_content = True
                        padding = repeat(Space, line_indent + doc.indent)
                        yield from map(self.emit, padding)
                        yield token

    ###########################################################################
    # Buffering
    ###########################################################################

    @contextmanager
    def buffering(self) -> Iterator[None]:
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
        return row_buffer

    def buffer_table(self, table: Table) -> TableBuffer:
        table_buffer = TableBuffer()
        table_buffer.extend(self.buffer_row(row) for row in table.rows)
        table_buffer.update()
        return table_buffer
