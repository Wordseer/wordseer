Pipeline path
=============

CollectionProcessor
-------------------

The entry point for data to be processed is at
:class:`~wordseerbackend.collectionprocessor`, specifically at
:meth:`~wordseerbackend.collectionprocessor.CollectionProcessor.process`.
``process`` interacts with the :class:`~wordseerbackend.logger` in order to
determine what to do, in this order:

1. Check if metadata and text has been extracted from documents. If not, then
call :meth:`~wordseerbackend.collectionprocessor.CollectionProcessor.\
extract_record_metadata`.

2. Check if the parser is configured to do grammatical processing (based on
information in :class:`~wordseerbackend.config`) and if so, if the processing
has been finished. If not, then call
:meth:`~wordseerbackend.collectionprocessor.CollectionProcessor.\
parse_documents`.

3. Check if the parser is configured to index sequences and if sequence
processing has been finished. If not, then call
:meth:`~wordseerbackend.collectionprocessor.CollectionProcessor.\
calculate_index_sequences` and then
``finish_indexing_sequences()`` on the database reader/writer.

4. Check if word counts have been finished. If not, call
``calculate_word_counts()`` on the reader/writer and record this task as
finished.

5. If the parser is configured to calculate TF IDFs, check and if this has been
done. If the parser still has to do this, call ``calculate_tfidfs()`` on the
reader/writer.

6. Check if the parser is configured to do word to word similarity calculations
and if they have been done yet. If it is and they haven't, then call
``calculate_lin_similarities`` on the reader/writer.

The methods listed above are the methods that interface with the real processing
code. Here is a short description of how they work and fit into the overall
pipeline.

:meth:`~wordseerbackend.collectionprocessor.CollectionProcessor.extract_record_metadata`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

