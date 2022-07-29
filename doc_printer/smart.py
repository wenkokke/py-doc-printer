from .typing import *
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

    @overrides
    def render(self, doc: Doc) -> TokenStream:
        if isinstance(doc, Alt) and len(doc.alts) > 1:
            yield from self.render_with_lookahead(doc.alts)
        else:
            yield from self.render_simple(doc)

    @overrides
    def emit(self, token: Token) -> Token:
        if self.is_buffering:
            return token
        else:
            if token is Line:
                self.line_width = 0
            else:
                self.line_width += len(token)
            if (
                self.raise_error_if_line_width_exceeded
                and self.line_width > self.max_line_width
            ):
                raise LineWidthExceeded
            return token

    @contextmanager
    def safe_mode(self) -> Iterator[None]:
        self.raise_error_if_line_width_exceeded = True
        try:
            yield None
        finally:
            self.raise_error_if_line_width_exceeded = False

    def render_with_lookahead(self, alts: tuple[Doc, ...]) -> TokenStream:
        default, *rest = alts
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
            yield from self.render(default)
