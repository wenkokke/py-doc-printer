Document Printer
----------------------------------------

A Wadler-Leijen Pretty Printer in Python.

.. automodule:: doc_printer.doc


Documents
=======================================


   .. autoclass:: Doc

      The abstract class for all documents.

   .. autodata:: DocLike

      DocLike is an alias for any type which can be coerced into a document:

      - a string;
      - a document;
      - a sequence of things that can be coerced into documents.

      Strings are converted using :meth:`Text.lines`.


Basic tokens
=======================================

   Text is the type for all concrete tokens in the document.

   Text tokens are assumed to be free from whitespaces and newlines, but the constructor cannot guarantee that. The safe way to construct tokens from unknown strings is to use :meth:`Text.lines`.

   .. autoclass:: Text
      :members: words, lines

      The type of string tokens.

   There are several singleton instances of :class:`Text`:

   .. autodata:: Empty

      The empty document.

   .. autodata:: Space

      Encodes all whitespace in the document.

   .. autodata:: Line

      Encodes all newlines in the document.


Concatenating documents
=======================================

   Two documents can be combined as ``doc1 / doc2`` or, separated by a space, as ``doc1 // doc2``.

   .. automethod:: Doc.__truediv__

   .. automethod:: Doc.__floordiv__

   There are corresponding implementations of ``__rtruediv__`` and ``__rfloordiv__``, so that either the left or the right argument to the operator can be a string.

   These methods are implemented in terms of :meth:`Doc.then`.

   .. automethod:: Doc.then

   A stream of documents can be combined with a separator using :meth:`Doc.join`.

   .. automethod:: Doc.join

   All of these methods are implemented in terms of :func:`cat`.

   .. autofunction:: cat

      Smart constructor for :class:`Cat`

   .. autoclass:: Cat

      The type of concatenated documents.


Parentheses
=======================================

   .. autofunction:: parens

   .. autofunction:: brackets

   .. autofunction:: braces

   .. autofunction:: angles

   .. autofunction:: quote


Alternative layout options
=======================================

   Two alternative layouts can be combined as `alt1 | alt2`.

   .. automethod:: Doc.__or__

   When alternatives are combined, it's important that the alternative whose first line is the shortest comes first.

   There is a corresponding implementations of ``__ror__``, so that either the left or the right argument to the operator can be a string.

   This method is implemented in terms of :func:`alt`.

   .. autofunction:: alt

      Smart constructor for :class:`Alt`

   .. autoclass:: Alt

      The type of alternate document layouts.

   There are several singleton instances of :class:`Alt`:

   .. autodata:: Fail

      The empty list of alternatives, meaning the current layout has failed.

   .. autodata:: SoftLine

      The optional newline, which lets the renderer know it is allowed to insert a newline in this place.


Identation
=======================================

   .. autoclass:: Nest

      The type of indented documents.


Alignment
=======================================

   Alignment is done via :class:`Row` and :class:`Table`.
   You can create tables using :func:`row` and :func:`table`.

   .. autofunction:: row

      Smart constructor for :class:`Row`.

   .. autofunction:: table

      Smart constructor for :class:`Table`.

   Alternatively, you can merge existing rows into a table using :func:`create_tables`.

   .. autofunction:: create_tables

      Merges sequences of rows with the same :data:`RowInfo.table_type` into a table, and inserts it as an alternative into the document.

   .. autoclass:: RowInfo
      :members: hpad, hsep, table_type

   .. autoclass:: Row

      The type of rows.

   .. autoclass:: Table

      The type of tables


Rendering
=======================================

Documents are rendered as a stream of :data:`doc_printer.typing.Token`, which are joined into a string by :data:`doc_printer.abc.DocRenderer.to_str`.

.. autodata:: doc_printer.typing.Token
.. autodata:: doc_printer.typing.TokenStream

.. automodule:: doc_printer.abc

   .. autoclass:: DocRenderer
      :members: to_str, render


Rendering Naively
=======================================


The simple renderer for documents ignores all alternatives, simply choosing the first alternative, which should have the shortest line length.

.. automodule:: doc_printer.simple

   .. autoclass:: SimpleDocRenderer
      :members: render_simple


Rendering Tables
=======================================

Tables are cached, to calculate their column widths and insert the appropriate spacing.

To create these buffers, :meth:`doc_printer.abc.DocRenderer.buffer_table` and :meth:`doc_printer.abc.DocRenderer.buffer_row` are provided.

.. automethod:: doc_printer.abc.DocRenderer.buffer_table

.. automethod:: doc_printer.abc.DocRenderer.buffer_row

Table buffers are rendered using the :meth:`doc_printer.table.TableBuffer.render`.

It is important to call :meth:`doc_printer.table.TableBuffer.update` once, just before rendering, as this calculates the needed column widths.

.. automodule:: doc_printer.table

   .. autoclass:: TableBuffer
      :members: append, extend, render, update

   .. autoclass:: RowBuffer
      :members: append, extend, render

   .. autoclass:: CellBuffer
      :members: append, extend, render


Rendering with Lookahead
=======================================

Finally, the smart renderer uses one level of lookahead.

When rendering a series of alternatives, it renders the first line of each alternative using the simple renderer, and picks the alternative that best fills up the current line.

.. automodule:: doc_printer.smart

   .. autoclass:: SmartDocRenderer
      :members: render_with_lookahead
