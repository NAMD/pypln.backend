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

import os
import unittest
from textwrap import dedent
from pypln.backend.workers import spellchecker

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


class TestSpellcheckerWorker(unittest.TestCase):
    def test_spellchek_pt(self):
        text = u"Meu cachoro é um pastor"
        errors = spellchecker.SpellingChecker().process({'text': text, 'language': 'pt_BR'})
        assert len(errors) == 1
        assert 'cachoro' in errors['spelling_errors'][0]
        assert 'cachorro' in errors['spelling_errors'][0][2]
        self.assertEqual(errors['spelling_errors'][0][1], 4)

