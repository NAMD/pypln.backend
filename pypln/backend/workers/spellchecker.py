# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.


import enchant
from enchant.checker import SpellChecker
from pypln.backend.celery_task import PyPLNTask

class SpellingChecker(PyPLNTask):
    """
    This worker performs spellchecking in the plain text of a document
    """
    def __init__(self):
        # This method is only called once per process, but that is no problem
        # since the enchant languange list should not change. Don't use this
        # method for anything that should run every time the task is called.
        # See http://docs.celeryproject.org/en/latest/userguide/tasks.html#instantiation
        # for more information.
        self.checkers = {lang: SpellChecker(lang) for lang in enchant.list_languages()}

    def process(self, document):
        #TODO: this worker may be enhanced by also checking the errors against an specific vocabulary supplied with the document
        try:
            checker = self.checkers[document['language']]
            checker.set_text(document['text'])
            errors = [[e.word, e.wordpos, e.suggest()] for e in checker]
        except KeyError:
            errors = None

        return {'spelling_errors': errors}

