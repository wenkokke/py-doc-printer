import abc
import collections.abc
import itertools

from .doc import *


class RenderError(Exception):
    pass


OnEmit = collections.abc.Callable[[Token], Token]


class DocRenderer(abc.ABC):
    def to_str(self, doc: Doc) -> str:
        return "".join(token.text for token in self.render(doc))

    @abc.abstractmethod
    def render(self, doc: Doc) -> TokenStream:
        """
        Render a document as a stream of tokens.
        """

    def render_stream(self, docs: collections.abc.Iterable[Doc]) -> TokenStream:
        yield from itertools.chain.from_iterable(map(self.render, docs))
