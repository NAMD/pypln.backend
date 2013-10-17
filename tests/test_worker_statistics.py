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

from pypln.backend.workers import Statistics


class TestStatisticsWorker(unittest.TestCase):
    def test_simple(self):
        sentences = [['this', 'is', 'a', 'test', '.'],
                     ['this', 'is', 'another', '!']]
        freqdist = [('this', 2), ('is', 2), ('a', 1), ('test', 1), ('.', 1),
                    ('another', 1), ('!', 1)]
        result = Statistics().process({'freqdist': freqdist,
                                       'sentences': sentences})
        self.assertEqual(result['average_sentence_length'], 4.5)
        self.assertEqual(result['average_sentence_repertoire'], 1)
        self.assertEqual(result['momentum_3'], 3)

    def test_zero_division_error(self):
        result = Statistics().process({'freqdist': [], 'sentences': []})
        for value in result.values():
            self.assertEqual(value, 0)
