Data Gathering and Importing
============================

**WARNING:** since we rebuilt our backend, this documentation is depreacted.
Come here in some days and we'll have an updated one.

The main goal of PyPLN is to analyze textual data coming from all kinds of documents. Therefore, an essencial pre-requisite to its use is
gathering some collection of documents which can then be imported to PyPLN Mongodb document store in order to be analyzed.

To help achieve this goal, PyPLN provides some tools for data gathering and importing. Here we will cover some of these tools and also describe some of the already supported sources of documents that one might want to tap into.

Document Sources
----------------
The sources described here are already supported for fetching and importing, or are in the process of analysis to be included among the fully supported sources. Those in development shold be clearly marked so.

Scientific Publications
~~~~~~~~~~~~~~~~~~~~~~~

*PubMedCentral* (In development)
    This repository contais close to 2 million articles from multiple open access `journals <http://www.ncbi.nlm.nih.gov/pmc/journals/?filter=t1#csvfile>`_. The ful text of the articles is available via `FTP <http://www.ncbi.nlm.nih.gov/pmc/tools/ftp/>`_ (for full text, PDFs, and supplementary data files, if any) or through an `OAI service <http://www.ncbi.nlm.nih.gov/pmc/tools/oai/>`_ for full articles in XML format.


Document Gathering Tools
------------------------
Automatic download of documents require some kind of software which is normally distributed along with PyPLN sources. Listed Below are the document fetching tools already available with a link to their full documentation.

Document Importing Tools
------------------------
For every document type, an importing tool is required to add the document do aour Mongodb store. Listed below are the importing tools already available with a link to their full documentation.
