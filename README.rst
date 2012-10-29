PyPLN
=====

PyPLN is a distributed pipeline for natural language processing, made in Python.
We use `NLTK <http://nltk.org/>`_ and `ZeroMQ <http://www.zeromq.org/>`_ as
our foundations. The goal of the project is to create an easy way to use NLTK
for processing big corpora, with a Web interface.

We don't have a production release yet, but it's scheduled on our
`next milestone <https://github.com/namd/pypln/issues?milestone=1>`_.


Documentation
-------------

Our documentation is hosted using `GitHub Pages <http://pages.github.com/>`_:

- `PyPLN Documentation <http://namd.github.com/pypln/>`_
  (created using `Sphinx <http://sphinx.pocoo.org/>`_)
- `Code reference <http://namd.github.com/pypln/reference/>`_
  (created using `epydoc <http://epydoc.sourceforge.net/>`_)


Requirements
------------

To install dependencies (on a Debian-like GNU/Linux distribution)::

    sudo apt-get install python-setuptools
    pip install virtualenv virtualenvwrapper
    mkvirtualenv pypln
    pip install -r requirements/production.txt

You will also need to install NLTK data. You can do so following the `NLTK
documentation <http://nltk.org/data.html>`_.


Developing
----------

To run tests::

    workon pypln
    pip install -r requirements/development.txt
    make test


..  TODO: The PYTHONPATH issue should be fixed once we organize the directory
    structure. As soon as this is fixed, we must update this instructions.

To run the development webserver::

    workon pypln
    cd pypln/web/
    pip install -r requirements/project.txt
    PYTHONPATH="../../:$PYTHONPATH" ./manage.py runserver --settings=settings.development



See our `code guidelines <https://github.com/namd/pypln/blob/develop/CONTRIBUTING.rst>`_.
