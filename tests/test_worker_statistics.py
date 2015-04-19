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

from pypln.backend.workers import Statistics
from utils import TaskTest


class TestStatisticsWorker(TaskTest):
    def test_simple(self):
        self.document['sentences'] = [['this', 'is', 'a', 'test', '.'],
                     ['this', 'is', 'another', '!']]
        self.document['freqdist'] = [('this', 2), ('is', 2), ('a', 1),
                ('test', 1), ('.', 1), ('another', 1), ('!', 1)]
        Statistics().delay(self.fake_id)
        self.assertEqual(self.document['average_sentence_length'], 4.5)
        self.assertEqual(self.document['average_sentence_repertoire'], 1)
        self.assertAlmostEqual(self.document['momentum_1'], 1.2857, places=3)
        self.assertAlmostEqual(self.document['momentum_2'], 1.8571, places=3)
        self.assertEqual(self.document['momentum_3'], 3)
        self.assertAlmostEqual(self.document['momentum_4'], 5.2857, places=3)
        self.assertAlmostEqual(self.document['repertoire'], 0.7777, places=3)

    def test_zero_division_error(self):
        self.document.update({'freqdist': [], 'sentences': []})
        Statistics().delay(self.fake_id)
        self.assertEqual(self.document['average_sentence_length'], 0)
        self.assertEqual(self.document['average_sentence_repertoire'], 0)
        self.assertEqual(self.document['momentum_1'], 0)
        self.assertEqual(self.document['momentum_2'], 0)
        self.assertEqual(self.document['momentum_3'], 0)
        self.assertEqual(self.document['momentum_4'], 0)
        self.assertEqual(self.document['repertoire'], 0)
