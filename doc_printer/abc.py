from abc import ABC, abstractmethod
from itertools import chain

from .doc import *
from .typing import *
from .table import *


class DocRenderer(ABC):
    def to_str(self, doc: Doc) -> str:
        return "".join(token.text for token in self.render(doc))

    @abstractmethod
    def render(self, doc: Doc, *, on_emit: OnEmit | None = None) -> TokenStream:
        """
        Render a document as a stream of tokens.
        """

    def render_stream(
        self, docs: Iterable[Doc], *, on_emit: OnEmit | None = None
    ) -> TokenStream:
        yield from chain.from_iterable(
            self.render(doc, on_emit=on_emit) for doc in docs
        )

    def buffer_row(self, row: Row) -> RowBuffer:
        row_buffer = RowBuffer(
            hsep=row.info.hsep, min_col_widths=row.info.min_col_widths
        )
        for cell in row.cells:
            cell_buffer = CellBuffer(hpad=row.info.hpad)
            cell_buffer.extend(self.render(cell, on_emit=None))
            row_buffer.append(cell_buffer)
        return row_buffer

    def buffer_table(self, table: Table) -> TableBuffer:
        table_buffer = TableBuffer()
        table_buffer.extend(self.buffer_row(row) for row in table.rows)
        table_buffer.update()
        return table_buffer
