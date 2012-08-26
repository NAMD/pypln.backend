Data Gathering and Importing
============================

The main goal of PyPLN is to analyze textual data coming from all kinds of documents. Therefore, an essential pre-requisite to its use is
gathering some collection of documents which can then be imported to PyPLN document store in order to be analyzed.

To help achieve this goal, PyPLN provides some tools for data gathering and importing. Here we will cover some of these tools and also describe some of the already supported sources of documents that one might want to tap into.

Document Sources
----------------
The sources described here are already supported for fetching and importing, or are in the process of analysis to be included among the fully supported sources. Those in development should be clearly marked so.

Scientific Publications
~~~~~~~~~~~~~~~~~~~~~~~

*PubMedCentral* (In development)
    This repository contais close to 2 million articles from multiple open access `journals <http://www.ncbi.nlm.nih.gov/pmc/journals/?filter=t1#csvfile>`_. The ful text of the articles is available via `FTP <http://www.ncbi.nlm.nih.gov/pmc/tools/ftp/>`_ (for full text, PDFs, and supplementary data files, if any) or through an `OAI service <http://www.ncbi.nlm.nih.gov/pmc/tools/oai/>`_ for full articles in XML format.

Documents in the File System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Files can be uploaded through the web interface either one by one or as a zipped collection of documents. PyPLN will then extract the text from these documents and add them to a collection. The documents are also kept in the original format, so that the file can be re-analyzed when new versions of the extractor worker are made available.


Bulk loading of ocuments
---- ---------------------

While the use of the web interface is very simple and usable for corpus creation, it may not be practical for loading large collections of texts. PyPLN include scrpits for fast loading of large collections of documents. These scripts can be found in the scripts directory in the package.
