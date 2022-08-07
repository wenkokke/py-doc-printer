import collections.abc
import contextlib
import dataclasses

from .doc import *
from .simple import *


class LineWidthExceeded(Exception):
    pass


@dataclasses.dataclass
class SmartDocRenderer(SimpleDocRenderer):
    max_line_width: int = 80

    def render(self, doc: Doc) -> TokenStream:
        if isinstance(doc, Alt) and len(doc.alts) > 1:
            yield from self.render_with_lookahead(doc.alts)
        else:
            yield from self.render_simple(doc)

    ###########################################################################
    # Strict Mode & Raising Errors when Max Line Width is Exceeded
    ###########################################################################

    is_strict: bool = dataclasses.field(default=False, init=False)

    def strict_emit(self, token: Token) -> Token:
        if self.column + len(token) > self.max_line_width:
            raise LineWidthExceeded()
        else:
            return token

    @contextlib.contextmanager
    def strict(self) -> collections.abc.Iterator[None]:
        self.on_emit.append(self.strict_emit)
        try:
            yield None
        finally:
            self.on_emit.remove(self.strict_emit)

    def render_with_lookahead(self, alts: tuple[Doc, ...]) -> TokenStream:
        fallback, *rest = alts
        succeeded = False
        for alt in reversed(rest):
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
