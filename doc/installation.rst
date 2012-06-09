Installing PyPLN
================

**WARNING:** since we rebuilt our backend, this documentation is depreacted.
Come here in some days and we'll have an updated one.

Installing PyPLN can vary in complexity depending one the functionality one needs to enable. It can be as simple as Python Packge installation or require complex configurations of a cluster of machines for distributed processing. Besides this PyPLN also has a web frontend which can be deployed to provide a user-friendly interface to its functionality.

Beside the main code, PyPLN also requires a Mongodb server to hold the data it uses and produces.

Installing the Package
----------------------

PyPLN main releases are always available on Python Package Index (PyPI), and can be installed with the following command::

    $ sudo easy_install -U pypln

or::

    $ sudo pip install --upgrade pypln

Setting up Mongodb
------------------

