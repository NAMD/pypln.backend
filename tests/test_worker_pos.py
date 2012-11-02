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
from pypln.backend.workers import POS


class TestPosWorker(unittest.TestCase):
    def test_pos_should_return_a_list_of_tuples_with_token_classification_and_offset(self):
        text = 'The sky is blue, the sun is yellow.'
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']
        expected = [('The', 'DT', 0), ('sky', 'NN', 4), ('is', 'VBZ', 8),
                   ('blue', 'JJ', 11), (',', ',', 15), ('the', 'DT', 17),
                   ('sun', 'NN', 21), ('is', 'VBZ', 25), ('yellow', 'JJ', 28),
                   ('.', '.', 34)]
        result = POS().process({'text': text, 'tokens': tokens,
                                'language': 'en'})
        self.assertEqual(result, {'pos': expected})

