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
from textwrap import dedent
from pypln.backend.workers import spellchecker
from utils import TaskTest

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


class TestSpellcheckerWorker(TaskTest):
    def test_spellchek_pt(self):
        text = u"Meu cachoro é um pastor"
        doc_id = self.collection.insert({'text': text, 'language': 'pt_BR'},
                w=1)
        spellchecker.SpellingChecker().delay(doc_id)

        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertEqual(len(refreshed_document['spelling_errors']), 1)
        self.assertIn('cachoro', refreshed_document['spelling_errors'][0])
        self.assertIn('cachorro', refreshed_document['spelling_errors'][0][2])
        self.assertEqual(refreshed_document['spelling_errors'][0][1], 4)

    def test_spellchek_en(self):
        text = u"The cat bit the doggyo"
        doc_id = self.collection.insert({'text': text, 'language': 'en'}, w=1)
        spellchecker.SpellingChecker().delay(doc_id)

        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertEqual(len(refreshed_document['spelling_errors']), 1)
        self.assertIn('doggyo', refreshed_document['spelling_errors'][0])
        self.assertIn('doggy', refreshed_document['spelling_errors'][0][2])
        self.assertEqual(refreshed_document['spelling_errors'][0][1], 16)

