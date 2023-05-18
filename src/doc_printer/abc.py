import abc
from typing import Callable, Iterable

from ._compat_itertools import chain
from .doc import *


class RenderError(Exception):
    pass


OnEmit = Callable[[Token], Token]


class DocRenderer(abc.ABC):
    def to_str(self, doc: Doc) -> str:
        return "".join(token.text for token in self.render(doc))

    @abc.abstractmethod
    def render(self, doc: Doc) -> TokenStream:
        """
        Render a document as a stream of tokens.
        """

    def render_stream(self, docs: Iterable[Doc]) -> TokenStream:
        yield from chain.from_iterable(map(self.render, docs))
