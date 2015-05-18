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


from textwrap import dedent

from pypln.backend.workers import Lemmatizer
from utils import TaskTest


class TestLemmatizerWorker(TaskTest):

    def test_lemmatizer_should_return_a_list_with_lemmas(self):
        palavras_output = dedent('''
        Eu\t[eu] <*> PERS M/F 1S NOM @SUBJ>  #1->2
        sei\t[saber] <fmc> <mv> V PR 1S IND VFIN @FS-STA  #2->0
        que\t[que] <clb> <clb-fs> KS @SUB  #3->7
        em\t[em] <sam-> PRP @PIV>  #4->7
        este\t[este] <-sam> <dem> DET M S @>N  #5->6
        momento\t[momento] <dur> <f-q> N M S @P<  #6->4
        falo\t[falar] <vH> <mv> V PR 1S IND VFIN @FS-<ACC  #7->2
        para\t[para] PRP @<ADVL  #8->7
        todo\t[todo] <quant> DET M S @>N  #9->10
        Brasil\t[Brasil] <civ> <newlex> <*> PROP M S @P<        [Brasil] <*> PROP M S @P<  #10->8
        $. #11->0
        </s>
        ''').strip() + '\n\n'

        self.document['palavras_raw'] = palavras_output
        self.document['palavras_raw_ran'] = True
        result = Lemmatizer().delay(self.fake_id)
        expected = 'eu saber que em este momento falar para todo Brasil .'.split()
        self.assertEqual(self.document['lemmas'], expected)
