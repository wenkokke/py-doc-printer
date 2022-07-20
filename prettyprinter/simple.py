from functools import singledispatchmethod
from .doc import *
from .typing import *
from .abc import *
from .table import *


@dataclass
class SimpleDocRenderer(DocRenderer):
    @overrides
    def render(self, doc: Doc, *, on_emit: OnEmit | None = None) -> TokenStream:
        yield from self.render_simple(doc, on_emit=on_emit)

    @singledispatchmethod
    def render_simple(self, doc: Doc, *, on_emit: OnEmit | None = None) -> TokenStream:
        raise TypeError(type(doc))

    @render_simple.register
    def _(self, doc: Text, *, on_emit: OnEmit | None = None) -> TokenStream:
        yield on_emit(doc) if on_emit else doc

    @render_simple.register
    def _(self, doc: Alt, *, on_emit: OnEmit | None = None) -> TokenStream:
        if doc.alts:
            yield from self.render(doc.alts[0], on_emit=on_emit)
        else:
            return RenderError(doc)

    @render_simple.register
    def _(self, doc: Cat, *, on_emit: OnEmit | None = None) -> TokenStream:
        yield from self.render_stream(doc.docs, on_emit=on_emit)

    @render_simple.register
    def _(self, doc: Row, *, on_emit: OnEmit | None = None) -> TokenStream:
        yield from self.buffer_row(doc).render(on_emit=on_emit)
        yield on_emit(Line) if on_emit else Line

    @render_simple.register
    def _(self, doc: Table, *, on_emit: OnEmit | None = None) -> TokenStream:
        yield from self.buffer_table(doc).render(on_emit=on_emit)

    @render_simple.register
    def _(self, doc: Nest, *, on_emit: OnEmit | None = None) -> TokenStream:
        has_content: bool = False
        line_indent: int = 0
        for token in self.render(doc.doc, on_emit=on_emit):
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
                        yield from map(on_emit, padding) if on_emit else padding
                        yield token
