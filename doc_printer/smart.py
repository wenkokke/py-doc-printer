from contextlib import contextmanager
from .simple import *
from .doc import *


class LineWidthExceeded(Exception):
    pass


@dataclass
class SmartDocRenderer(SimpleDocRenderer):
    max_line_width: int = 80

    raise_error_if_line_width_exceeded: bool = field(
        default=False, init=False, repr=False
    )

    # @overrides
    def render(self, doc: Doc) -> TokenStream:
        if isinstance(doc, Alt) and len(doc.alts) > 1:
            yield from self.render_with_lookahead(doc.alts)
        else:
            yield from self.render_simple(doc)

    def line_width_exceeded(self, token: Token) -> Token:
        if self.line_width > self.max_line_width:
            raise LineWidthExceeded()
        else:
            return token

    @contextmanager
    def safe_mode(self) -> Iterator[None]:
        self.on_emit.append(self.line_width_exceeded)
        try:
            yield None
        finally:
            self.on_emit.remove(self.line_width_exceeded)

    def render_with_lookahead(self, alts: tuple[Doc, ...]) -> TokenStream:
        fallback, *rest = alts
        succeeded = False
        for alt in reversed(rest):
            try:
                with self.safe_mode():
                    buffer = list(self.render_simple(alt))
                    succeeded = True
                    yield from buffer
            except LineWidthExceeded:
                continue
        if not succeeded:
            yield from self.render(fallback)
