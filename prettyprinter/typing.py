from collections.abc import Callable, Iterator
from .doc import *

import typing


class RenderError(Exception):
    pass


Token: typing.TypeAlias = Text
TokenStream: typing.TypeAlias = Iterator[Token]
TokenBuffer: typing.TypeAlias = list[Token]

OnEmit: typing.TypeAlias = Callable[[Token], Token]
