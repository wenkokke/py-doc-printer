from abc import ABC, abstractmethod
from contextlib import contextmanager
from itertools import chain

from .doc import *
from .typing import *
from .table import *


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
