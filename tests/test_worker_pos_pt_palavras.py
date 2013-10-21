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

import unittest

from textwrap import dedent

from pypln.backend.workers.pos import pt_palavras


class TestPosWorker(unittest.TestCase):
    def test_should_return_None_if_palavras_raw_does_not_exist(self):
        result = pt_palavras.pos({'text': 'Isso é um teste.'})
        expected = '', []
        self.assertEqual(result, expected)

    def test_(self):
        palavras_output = dedent('''
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
        expected = ('pt-palavras', [('Eu', 'PERS'), ('sei', 'V'), ('que', 'KS'),
                    ('em', 'PRP'), ('este', 'DET'), ('momento', 'N'),
                    ('falo', 'V'), ('para', 'PRP'), ('todo', 'DET'),
                    ('Brasil', 'PROP'), ('.', '.')])
        result = pt_palavras.pos({'text': 'anything',
            'palavras_raw': palavras_output})
        self.assertEqual(expected, result)
