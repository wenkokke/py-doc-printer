from abc import ABC, abstractmethod
from contextlib import contextmanager
from itertools import chain

from .doc import *
from .typing import *
from .table import *


class DocRenderer(ABC):
    def __init__(self):
        self.is_buffering: bool = False

    def to_str(self, doc: Doc) -> str:
        return "".join(token.text for token in self.render(doc))

    def emit(self, token: Token) -> Token:
        return token

    @abstractmethod
    def render(self, doc: Doc) -> TokenStream:
        """
        Render a document as a stream of tokens.
        """

    def render_stream(self, docs: Iterable[Doc]) -> TokenStream:
        yield from chain.from_iterable(self.render(doc) for doc in docs)

    @contextmanager
    def buffering(self) -> Iterator[None]:
        self.is_buffering = True
        try:
            yield None
        finally:
            self.is_buffering = False

    def buffer(self, doc: Doc) -> TokenStream:
        with self.buffering():
            yield from self.render(doc)

    def buffer_row(self, row: Row) -> RowBuffer:
        row_buffer = RowBuffer(
            hsep=row.info.hsep, min_col_widths=row.info.min_col_widths
        )
        for cell in row.cells:
            cell_buffer = CellBuffer(hpad=row.info.hpad)
            cell_buffer.extend(self.buffer(cell))
            row_buffer.append(cell_buffer)
        return row_buffer

    def buffer_table(self, table: Table) -> TableBuffer:
        table_buffer = TableBuffer()
        table_buffer.extend(self.buffer_row(row) for row in table.rows)
        table_buffer.update()
        return table_buffer
