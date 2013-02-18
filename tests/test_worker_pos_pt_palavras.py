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
    def test_(self):
        palavras_output = dedent('''
        $START
        Eu\t[eu] <*> PERS M/F 1S NOM @SUBJ>
        sei\t[saber] V PR 1S IND VFIN @FMV
        que\t[que] KS @#FS-<ACC @SUB
        em\t[em] <sam-> PRP @PIV>
        este\t[este] <-sam> <dem> DET M S @>N
        momento\t[momento] <dur> <f-q> N M S @P<
        falo\t[falar] <vH> V PR 1S IND VFIN @FMV
        para\t[para] PRP @<ADVL
        todo\t[todo] <quant> DET M S @>N
        Brasil\t[Brasil] <*> <newlex> PROP M S @P< \t[Brasil] <*> PROP M S @P<
        $.
        ''').strip()
        expected = ('pt-palavras', [('Eu', 'PERS'), ('sei', 'V'), ('que', 'KS'),
                    ('em', 'PRP'), ('este', 'DET'), ('momento', 'N'),
                    ('falo', 'V'), ('para', 'PRP'), ('todo', 'DET'),
                    ('Brasil', 'PROP'), ('.', '.')])
        pt_palavras.call_palavras = lambda x: palavras_output
        result = pt_palavras.pos({'text': 'anything'})
        self.assertEqual(expected, result)
