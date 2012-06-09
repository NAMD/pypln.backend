Text Extraction and Normalization
=================================

**WARNING:** since we rebuilt our backend, this documentation is depreacted.
Come here in some days and we'll have an updated one.

The functioning of PyPLN's analytical pipeline starts depends on the existence of a collection raw text documents in Unicode encoding. such a collection, frequently is derived from a collection of text containing files in a variety of formats. In order to extract the text from a given file, we first need to find out its mimetype, and then invoke the appropriate program which is able to extract the text from it.

In PyPLN, we intend to handle a variety of document formats, but these extractors will be added gradually.
