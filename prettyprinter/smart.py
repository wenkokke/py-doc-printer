from .typing import *
from .simple import *
from .doc import *


class LineWidthExceeded(Exception):
    pass


@dataclass
class SmartDocRenderer(SimpleDocRenderer):
    max_line_width: int = 80
    line_width: int = field(default=0, init=False, repr=False)

    @overrides
    def to_str(self, doc: Doc) -> str:
        return "".join(token.text for token in self.render(doc, on_emit=self.emit))

    @overrides
    def render(self, doc: Doc, *, on_emit: OnEmit | None = None) -> TokenStream:
        if isinstance(doc, Alt) and len(doc.alts) > 1:
            yield from self.render_with_lookahead(doc.alts)
        else:
            yield from self.render_simple(doc, on_emit=on_emit)

    def emit(self, token: Token) -> Token:
        if token is Line:
            self.line_width = 0
        else:
            self.line_width += len(token)
        return token

    def safe_emit(self, token: Token) -> Token:
        token = self.emit(token)
        if self.line_width > self.max_line_width:
            raise LineWidthExceeded
        return token

    def render_with_lookahead(self, alts: tuple[Doc, ...]) -> TokenStream:
        default, *rest = alts
        succeeded = False
        for alt in reversed(rest):
            try:
                buffer = list(self.render_simple(alt, on_emit=self.safe_emit))
                succeeded = True
                yield from buffer
            except LineWidthExceeded:
                continue
        if not succeeded:
            yield from self.render(default)
