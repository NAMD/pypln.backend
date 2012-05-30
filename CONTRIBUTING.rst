Contributing
============

Contact Information
-------------------

You can interact with us through:

- IRC: `#pypln @ irc.freenode.net <http://webchat.freenode.net?channels=pypln>`_
- Mail list: `pypln @ Google Groups <https://groups.google.com/group/pypln>`_


Code Guidelines
---------------

- Use `PEP8 <http://www.python.org/dev/peps/pep-0008/>`_.
- `Commented code is dead code <http://www.codinghorror.com/blog/2008/07/coding-without-comments.html>`_.
- Write tests (preferably use `test-driven development <https://en.wikipedia.org/wiki/Test-driven_development>`_).
- Name identifiers (variable, class, function, module names) with readable
  names (``x`` is always wrong).
- Use `Python's new-style formatting <http://docs.python.org/library/string.html#format-string-syntax>`_
  (``'{} = {}'.format(a, b)`` instead of ``'%s = %s' % (a, b)``).
- All ``#TODO`` should be translated in issues (use our
  `GitHub issue system <https://github.com/namd/pypln/issues>`_).
- Run all tests before pushing (just execute ``make test``).

Git Usage
---------

- We use `git flow <https://github.com/nvie/gitflow>`_, so you must (learn more
  about this `successul Git branching model <http://nvie.com/posts/a-successful-git-branching-model/>`_).
- Please `write decent commit messages <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.
