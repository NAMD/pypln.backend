Storage Backend
===============

PyPLN can make use of various storage formats for both documents and analytical results. Since PyPLN is built with distributed processing in mind. The configuration of storage backends should, whenever possible be distributed as well. That is all databases should be available to workers and sinks as local resources, but at the same  time be part of a distributed infrastructure, being equally available to all machines in the cluster.

Whenever possible, we will use MongoDb Document database to handle storage, due to simplicity of its deployment and usage on distributed environments.

File Storage
----------------

For PyPLN, document storage happens at more than one stage of of the pipeline. At the beginning, we have the document files in their original formats prior to the text extraction phase. To avoid resorting to specific implementations of distributed filesystems, we use instead GridFS which transparently handles distribution of files across the cluster without the need of extra configurations.

Document Storage
--------------------------
For storing the raw text  versions of the files, PyPLN takes advantage of the schemaless nature of MongoDb. MongoDb Collections are sets of JSON (BSON) object, which in our case will be constructed gradually. Initially a text Document in a Mongo collection will have only one these fields::

    {'filename':'mydoc.pdf',
        'text':'...'
    }

Later down the pipeline, pre-processed versions of the text can be stored for further analysys.



