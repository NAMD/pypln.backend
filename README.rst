PyPLN
=====

PyPLN is a distributed pipeline for natural language processing, made in Python.
We use `NLTK <http://nltk.org/>`_ and `Celery <http://www.celeryproject.org>`_ as
our foundations. The goal of the project is to create an easy way to use NLTK
for processing big corpora, with a Web interface.

PyPLN is sponsored by `Fundação Getulio Vargas <http://portal.fgv.br/>`_.

License
-------

PyPLN is free software, released under the GPLv3
`<https://gnu.org/licenses/gpl-3.0.html>`_.


Documentation
-------------

Our documentation is hosted using `GitHub Pages <http://pages.github.com/>`_:

- `PyPLN Documentation <http://pypln.org/docs>`_
  (created using `Sphinx <http://sphinx.pocoo.org/>`_)
- `Code reference <http://pypln.org/docs/reference/>`_
  (created using `epydoc <http://epydoc.sourceforge.net/>`_)


Requirements
------------
You will need some Python packages, `libmagic <http://www.darwinsys.com/file/>`_,
 `poppler utils <http://poppler.freedesktop.org/>`_,
 `libfreetype <http://www.freetype.org/>`'s development headers and `aspell
 dictionaries <ftp://ftp.gnu.org/gnu/aspell/dict/0index.html.>`_ for english
 and portuguese.

To install dependencies (on a Debian-like GNU/Linux distribution)::

    sudo apt-get install python-setuptools libmagic-dev poppler-utils libfreetype6-dev fonts-dejavu aspell-en aspell-pt
    pip install virtualenv virtualenvwrapper
    mkvirtualenv pypln.backend
    # we need to install Cython first because of the way pip handles C extensions
    pip install Cython
    pip install -r requirements/production.txt

You will also need to download some NLTK data packages. You can do so
executing::

    python -m nltk.downloader genesis maxent_treebank_pos_tagger punkt stopwords averaged_perceptron_tagger



Developing
----------

To run tests::

    workon pypln.backend
    pip install -r requirements/development.txt
    make test

See our `code guidelines <https://github.com/namd/pypln.backend/blob/develop/CONTRIBUTING.rst>`_.

Creating a new Task
~~~~~~~~~~~~~~~~~~~

All analyses in PyPLN are performed by our workers. Every worker is a Celery
task that can be included in the canvas that will run when a document is
received in pypln.web.

New workers are very easy to create. All you need to do is write a subclass of `PyPLNTask <https://github.com/NAMD/pypln.backend/blob/develop/pypln/backend/celery_task.py#L36>`
that implements a "process" method. This method will receive the document as a
dictionary, and should return a dictionary that will be used to update the
existing document. As an example::


    from pypln.backend.celery_task import PyPLNTask

    class FreqDist(PyPLNTask):
        def process(self, document):
            value = document['value']
            square = value ** 2
            return {'squared_value': square}


This worker assumes that a previous worker has already included "value" in the
document and uses it to create a new one, called "squared_value".




