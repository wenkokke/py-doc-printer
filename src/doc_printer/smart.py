from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from ._compat_singledispatchmethod import singledispatchmethod
from .doc import *
from .simple import *


class LineWidthExceeded(Exception):
    pass


@dataclass
class SmartDocRenderer(SimpleDocRenderer):
    max_line_width: int = 80

    def render(self, doc: Doc) -> TokenStream:
        yield from self.render_with_lookahead(doc)

    ###########################################################################
    # Strict Mode & Raising Errors when Max Line Width is Exceeded
    ###########################################################################

    is_strict: bool = field(default=False, init=False)

    def strict_emit(self, token: Token) -> Token:
        if self.column + len(token) > self.max_line_width:
            raise LineWidthExceeded()
        else:
            return token

    @contextmanager
    def strict(self) -> Iterator[None]:
        self.on_emit.append(self.strict_emit)
        try:
            yield None
        finally:
            self.on_emit.remove(self.strict_emit)

    @singledispatchmethod
    def render_with_lookahead(
        self, doc: Doc, *, width_hint: WidthHint = Unknown
    ) -> TokenStream:
        yield from self.render_simple(doc)

    @render_with_lookahead.register
    def _(self, doc: Cat, *, width_hint: WidthHint = Unknown) -> TokenStream:
        for subdoc_width_hint, subdoc in zip(
            doc.width_hints(initial=width_hint), doc.docs
        ):
            yield from self.render_with_lookahead(subdoc, width_hint=subdoc_width_hint)

    @render_with_lookahead.register
    def _(self, doc: Alt, *, width_hint: WidthHint = Unknown) -> TokenStream:
        fallback, *alts = doc.alts
        succeeded = False
        for alt in reversed(alts):
            with self.strict():
                try:
                    token_stream = self.render_simple(alt)
                    token_buffer = self.buffer_stream(token_stream)
                except LineWidthExceeded:
                    continue
                succeeded = True
                yield from map(self.emit, token_buffer)
                break
        if not succeeded:
            yield from self.render(fallback)
