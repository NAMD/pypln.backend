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

from unittest import skipIf

from textwrap import dedent
from pypln.backend.workers.palavras_raw import palavras_installed
from pypln.backend.workers import POS
from utils import TaskTest


class TestPosWorker(TaskTest):
    def test_pos_should_return_a_list_of_tuples_with_token_classification_and_offset(self):
        text = 'The sky is blue, the sun is yellow.'
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']
        expected = [['The', 'DT', 0], ['sky', 'NN', 4], ['is', 'VBZ', 8],
                   ['blue', 'JJ', 11], [',', ',', 15], ['the', 'DT', 17],
                   ['sun', 'NN', 21], ['is', 'VBZ', 25], ['yellow', 'JJ', 28],
                   ['.', '.', 34]]
        doc_id = self.collection.insert({'text': text, 'tokens': tokens,
                                'language': 'en'}, w=1)
        POS().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertEqual(refreshed_document['pos'], expected)
        self.assertEqual(refreshed_document['tagset'], 'en-nltk')

    @skipIf(not palavras_installed(), 'palavras software is not installed')
    def test_pos_should_run_pt_palavras_if_text_is_in_portuguese(self):
        text = 'Isso é uma frase em português.'
        tokens = ['Isso', 'é', 'uma', 'frase', 'em', 'português', '.']
        palavras_raw = dedent('''
            Isso    [isso] <*> <dem> SPEC M S @SUBJ>  #1->2
            é       [ser] <vK> <fmc> <mv> V PR 3S IND VFIN @FS-STA  #2->0
            uma     [um] <arti> DET F S @>N  #3->4
            frase   [frase] <act-s> <ac-cat> N F S @<SC  #4->2
            em=português    [em=português] <pp> ADV @<ADVL  #5->2
            $. #6->0
            </s>
        ''').strip() + '\n\n'

        # '.' is the only named entity here.
        expected = [[u'.', u'.', 29]]
        doc_id = self.collection.insert({'text': text, 'tokens': tokens,
            'language': 'pt', 'palavras_raw': palavras_raw}, w=1)
        POS().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertEqual(refreshed_document['pos'], expected)
        self.assertEqual(refreshed_document['tagset'], 'pt-palavras')
