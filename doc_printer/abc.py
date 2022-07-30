from abc import ABC, abstractmethod
from itertools import chain
from typing import TypeAlias

from .doc import *


class RenderError(Exception):
    pass


OnEmit: TypeAlias = Callable[[Token], Token]


class DocRenderer(ABC):
    def to_str(self, doc: Doc) -> str:
        return "".join(token.text for token in self.render(doc))

    @abstractmethod
    def render(self, doc: Doc) -> TokenStream:
        """
        Render a document as a stream of tokens.
        """

    def render_stream(self, docs: Iterable[Doc]) -> TokenStream:
        yield from chain.from_iterable(map(self.render, docs))
