Text Extraction and Normalization
=================================

By default, PyPLN runs all documents uploaded, through a pipeline which starts with the extraction of plain text and its conversion into Unicode.
Then the text is ready to be stored and fed to other analytical steps, such as tokenization, part-of-speech tagging, etc.

Currently PyPLN supports the following document formats, from which it can extract plain text:
- PDF
- HTML
- Text

Prior to extraction however, PyPLN does mimetype detection, to define the form of the extraction. New mimetypes can be supported by writing new workers to perform the text extraction.
