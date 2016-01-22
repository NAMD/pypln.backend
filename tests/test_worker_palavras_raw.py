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

from pypln.backend.workers import palavras_raw
from utils import TaskTest


ORIGINAL_PATH = palavras_raw.BASE_PARSER

class TestPalavrasRawWorker(TaskTest):

    def test_should_run_only_if_language_is_portuguese(self):
        doc_id = self.collection.insert({'text': 'There was a rock on the way.',
            'language': 'en'}, w=1)

        palavras_raw.PalavrasRaw().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertEqual(refreshed_document['palavras_raw_ran'], False)

    def test_palavras_not_installed(self):
        palavras_raw.BASE_PARSER = '/not-found'
        doc_id = self.collection.insert(
                {'text': 'Tinha uma pedra no meio do caminho.',
                    'language': 'pt'}, w=1)
        palavras_raw.PalavrasRaw().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertEqual(refreshed_document['palavras_raw_ran'], False)


    @skipIf(not palavras_raw.palavras_installed(), 'palavras software is not installed')
    def test_palavras_should_return_raw_if_it_is_installed(self):
        palavras_raw.BASE_PARSER = ORIGINAL_PATH
        doc_id = self.collection.insert(
                {'text': 'Eu sei que neste momento falo para todo Brasil.',
                    'language': 'pt'}, w=1)
        expected_raw = dedent('''
        Eu 	[eu] <*> PERS M/F 1S NOM @SUBJ>  #1->2
        sei 	[saber] <fmc> <mv> V PR 1S IND VFIN @FS-STA  #2->0
        que 	[que] <clb> <clb-fs> KS @SUB  #3->7
        em 	[em] <sam-> PRP @PIV>  #4->7
        este 	[este] <-sam> <dem> DET M S @>N  #5->6
        momento 	[momento] <dur> <f-q> N M S @P<  #6->4
        falo 	[falar] <vH> <mv> V PR 1S IND VFIN @FS-<ACC  #7->2
        para 	[para] PRP @<ADVL  #8->7
        todo 	[todo] <quant> DET M S @>N  #9->10
        Brasil 	[Brasil] <civ> <newlex> <*> PROP M S @P< 	[Brasil] <*> PROP M S @P<  #10->8
        $. #11->0
        </s>
        ''').strip() + '\n\n'
        result = palavras_raw.PalavrasRaw().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertEqual(refreshed_document['palavras_raw'], expected_raw)
        self.assertEqual(refreshed_document['palavras_raw_ran'], True)
