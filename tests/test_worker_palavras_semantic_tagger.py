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

from pypln.backend.workers import SemanticTagger
from utils import TaskTest


class TestSemanticTaggerWorker(TaskTest):

    def test_basic_semantic_tags(self):
        palavras_output = dedent('''
        Eu\t[eu] <*> PERS M/F 1S NOM @SUBJ>  #1->2
        sei\t[saber] <fmc> <mv> V PR 1S IND VFIN @FS-STA  #2->0
        que\t[que] <clb> <clb-fs> KS @SUB  #3->7
        em\t[em] <sam-> PRP @PIV>  #4->7
        este\t[este] <-sam> <dem> DET M S @>N  #5->6
        momento\t[momento] <dur> <f-q> N M S @P<  #6->4
        falo\t[falar] <vH> <mv> V PR 1S IND VFIN @FS-<ACC  #7->2
        para\t[para] PRP @<ADVL  #8->7
        todo=o\t[todo=o] <quant> DET M S @>N  #9->10
        povo\t[povo] <HH> N M S @P<  #10->8
        de\t[de] <sam-> <np-close> PRP @N<  #11->10
        o\t[o] <-sam> <artd> DET M S @>N  #12->13
        Brasil\t[Brasil] <civ> <*> PROP M S @P<  #13->11
        $. #14->0
        </s>
        ''').strip() + '\n\n'

        expected_tags = {
                 'Non_Tagged': ['Eu', 'sei', 'que', 'em', 'este', 'para',
                                'todo=o', 'de', 'o'],
                 'Collective': ['povo'],
                 'Time_Event': ['momento'],
                 'Place': ['Brasil'],
                 'Human': ['povo'],
                 'Verbs_related_human_things': ['falo']
        }

        self.document.update({'palavras_raw': palavras_output,
            'palavras_raw_ran': True})
        SemanticTagger().delay(self.fake_id)

        self.assertEqual(self.document['semantic_tags'], expected_tags)


    def test_ambiguous_tags(self):
        palavras_output = dedent('''
        Eu      [eu] <*> PERS M/F 1S NOM @SUBJ>  #1->2
        canto   [cantar] <vH> <fmc> <mv> V PR 1S IND VFIN @FS-STA  #2->0
        bem     [bem] <quant> ADV @<ADVL  #3->2
        enquanto        [enquanto] <clb> <clb-fs> <rel> <ks> ADV @ADVL>  #4->6
        ele     [ele] PERS M 3S NOM @SUBJ>  #5->6
        está    [estar] <mv> V PR 3S IND VFIN @FS-<ADVL  #6->2
        em      [em] <sam-> PRP @<SA  #7->6
        o       [o] <-sam> <artd> DET M S @>N  #8->9
        canto   [canto] <Labs> <act-d> <sem-l> <sem-r> N M S @P<  #9->7
        $. #10->0
        </s>
        ''').strip() + '\n\n'

        expected_tags = {
                'Non_Tagged': ['Eu', 'bem', 'enquanto', 'ele', 'está', 'em',
                               'o'],
                'Place and spatial': ['canto'],
                'Verbs_related_human_things': ['canto']
        }
        self.document.update({'palavras_raw': palavras_output,
            'palavras_raw_ran': True})
        SemanticTagger().delay(self.fake_id)
        self.assertEqual(self.document['semantic_tags'], expected_tags)
