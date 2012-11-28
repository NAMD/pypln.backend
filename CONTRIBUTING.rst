Contributing
============

Contact Information
-------------------

You can interact with us through:

- Mail list: `pypln @ Google Groups <https://groups.google.com/group/pypln>`_
- IRC: `#pypln @ irc.freenode.net <http://webchat.freenode.net?channels=pypln>`_


Code Guidelines
---------------

- **Please**, use `PEP8 <http://www.python.org/dev/peps/pep-0008/>`_.
- Write tests for every feature you add or bug you solve (preferably use
  `test-driven development <https://en.wikipedia.org/wiki/Test-driven_development>`_).
- `Commented code is dead code <http://www.codinghorror.com/blog/2008/07/coding-without-comments.html>`_.
- Name identifiers (variable, class, function, module names) with readable
  names (``x`` is always wrong).
- Use `Python's new-style formatting <http://docs.python.org/library/string.html#format-string-syntax>`_
  (``'{} = {}'.format(a, b)`` instead of ``'%s = %s' % (a, b)``).
- All ``#TODO`` should be translated in issues (use our
  `GitHub issue system <https://github.com/namd/pypln.backend/issues>`_).
- Run all tests before pushing (just execute ``make test``).
- Try to write Python3-friendly code, so when we decide to support both Python2
  and Python3, it'll not be a pain.


Git Usage
---------

- We use `git flow <https://github.com/nvie/gitflow>`_, so you must (learn more
  about this `successul Git branching model <http://nvie.com/posts/a-successful-git-branching-model/>`_).
- Please `write decent commit messages <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.


Generating Documentation
------------------------

We use the script ``make-docs.sh`` to generate documentation and it's served by
`GitHub Pages <http://pages.github.com/>`_. As we need to put **only the static
documentation files** on branch ``gh-pages``, our script does the job of:

- Stash (including untracked files) any non-commited modifications on current
  branch;
- Checkout to ``develop`` branch;
- Run `sphinx <http://sphinx.pocoo.org/>`_ and
  `epydoc <http://epydoc.sourceforge.net/>`_ to generate documentation;
- Copy generated documentation to another place (``/tmp/pypln-docs``);
- Check out to branch ``gh-pages``;
- Copy the static files to repository, add them and commit;
- Checkout back to the branch you were before running the script;
- Unstash the changes.

You can also generate documentation from your current branch (instead of
``develop``) or do not commit it (only generate). Please run ``./make-docs -h``
to know all the available options.

Note: epydoc's Bug
~~~~~~~~~~~~~~~~~~

If you get an exception when building documentation, probably it's an epydoc
bug. Please read
`this post on StackOverflow <http://stackoverflow.com/questions/6704770/epydoc-attributeerror-text-object-has-no-attribute-data>`_
and apply the proposed patch. Sorry, but it looks like it is not maintained
anymore.
