Introduction to PyPLN
=====================

PyPLN is a distributed pipeline architecture to analyze text. Conceptually, it was idealized to provide a complete analysis of textual documents in any format. A diagram of the currently envisioned analytical tasks can be seen on Figure :ref:`fig-cmap`.

.. _fig-cmap:
.. figure:: _static/pypln.png
   :width: 20cm

   Conceptual diagram of PyPLN

PyPLN makes use of well know text processing tools such as NLTK for natural language processing, and various other opensource tools for  text manipulation. PyPLN developers may develop new or improve existing tools for text/language processing but that is not the main development focus of the project. The main focus of PyPLN is providing a framework for efficient analysis of large collections of text. By efficient analysis we mean the combination of computational, mathematical and visualization techniques.

PyPLN relies heavily on distributed computing to be able to handle large collections of text. This distributed processing is built upon the ZeroMQ library and its API. Another key element to the scalability of our solution is the adoption of Mongodb for our storage backend. We use its replication and sharding capabilities to maximize I/O performance.

An very simplified example of the inner working of a text processing job in PyPLN is depicted on figure :ref:`fig-arch`.

.. _fig-arch:
.. figure:: _static/Pipeline_architecture.png
   :width: 20cm

   Example text processing job PyPLN.

Cluster Architecture
--------------------

Although PyPLN can be run on a single server, it should be configured to take advantage of a cluster of machines. Its basic architecture is illustrated on figure :ref:`fig-cluster`.

.. _fig-cluster:
.. figure:: _static/PyPLNcluster.png
   :width: 20cm

   General architecture of a PyPLN cluster


The cluster is managed by the manager process which interact with broker processes to distribute jobs to the cluster. Individual jobs are actualy managed by the broker processes running on each node os the cluster. Brokers start worker processes to run each job and monitor them for completion. If a worker hangs or takes too long to finish a job it can be killed have its job re-assigned.

The kinds of jobs PyPLN can run depend on its worker library. PyPLN comes with a set of basic workers, but users can easily write their own, as workers are very simple python scripts. (see :ref:`fig-worker` for example implementation). Since workers have full access to the underlying OS other executables can be started by a worker to do it's job.

.. _fig-worker:
.. figure:: _static/workercode.png
   :width: 20cm

   Simple code of a worker

Jobs can be chained in pipelines to realize more complex tasks. Currently, a single pipeline is available, but in the future, designing pipelines will be as simple as creating a worker.

Extending PyPLN
---------------

PyPLN can be extended through the implementation of new workers, and in the future new pipelines.

