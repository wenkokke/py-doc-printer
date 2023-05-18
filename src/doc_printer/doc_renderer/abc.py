import abc
from typing import Callable, Iterable, List

from mypy_extensions import mypyc_attr

from .._compat_itertools import chain
from ..doc import Doc, Token, TokenStream

__all__: List[str] = [
    "RenderError",
    "OnEmit",
    "DocRenderer",
]


class RenderError(Exception):
    pass


OnEmit = Callable[[Token], Token]


@mypyc_attr(allow_interpreted_subclasses=True)
class DocRenderer(metaclass=abc.ABCMeta):
    def to_str(self, doc: Doc) -> str:
        return "".join(token.text for token in self.render(doc))

    @abc.abstractmethod
    def render(self, doc: Doc) -> TokenStream:
        """
        Render a document as a stream of tokens.
        """

    def render_stream(self, docs: Iterable[Doc]) -> TokenStream:
        yield from chain.from_iterable(map(self.render, docs))
