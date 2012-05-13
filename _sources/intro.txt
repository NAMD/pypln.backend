Introduction to PyPLN
=====================

PyPLN is a distributed pipeline architecture to analyze text. Conceptually, it was idealized to provide a complete analysis of textual documents in any format. A diagram of the currently envisioned analytical tasks can be seen on Figure :ref:`fig-cmap`.

.. _fig-cmap:
.. figure:: _static/pypln.png
   :width: 20cm
   
   Conceptual diagram of PyPLN

This architecture is built upon the ZeroMQ library and its API.

An overview of the architecture as it currently stands is depicted on figure :ref:`fig-arch`.
    
.. _fig-arch:
.. figure:: _static/Pipeline_architecture.png
   :width: 20cm
   
   Current architecture of PyPLN.

The entire architecture is based on the existence of three basic types of components:

* Task ventilators
* Workers
* Sinks

Task ventilators are modules which are designed to receive a batch of tasks to be distributed. Ventilators are currently 
agnostic with regards to the type of tasks it is distributing. Tasks should be distributed along
with a task-type identification code, so that workers know which tasks they should fetch.
Currently, such task codes are yet to be defined so care must be taken to spawn the right type of workers for each task type.
A ventilator connects to a population of workers via a PUSH/PULL protocol, and data is distributed 
uniformly to workers via messages.

Workers are very simple programs which once started, listen continuously on the port opened by a Ventilator,
pull and processe data, pushing the results to a sink.

Extending PyPLN
---------------

PyPLN can be extended through the implementation of new worker, sink or ventilator modules. 
New workers and sinks should mimic the dummy implentations provided and must subclass BaseWorker and BaseSink, respectively.
