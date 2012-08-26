Storage Backend
===============

PyPLN makes use of MongoDB document database to handle storage of files and documents,
due to its scalability and performance characteristics.


File Storage
------------

For PyPLN, files access must be performant on a large cluster of nodes. To keep the deploymento of PyPLN as simple as possible, we resort to GridFS, MongoDB's distributed filesystem to store all files imported into PyPLN.


Document Storage
----------------

After text extraction, the raw text versions of the files and their analyses are store in a collection on MongoDB.
All documents are stored in a similar way in the database, basically just the raw text plus some metadata.

When a document passes through a pipeline, Analyses will be generated for it and stores in the analyses collection in the database along with the id of the documento it refers to.

.. figure:: _static/default-pipeline.png

   The PyPLN's default pipeline

