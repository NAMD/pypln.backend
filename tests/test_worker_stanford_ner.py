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
from pypln.backend.workers import StanfordNER


class TestStanfordNERWorker(unittest.TestCase):

    def test_ner_should_return_marked_entities(self):
        text = 'The sky is blue, the sun is yellow.'

        # Sample text from https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
        text = ("Dijkstra's algorithm, conceived by Dutch computer scientist "
            "Edsger Dijkstra in 1956 and published in 1959,[1][2] is a graph "
            "search algorithm that solves the single-source shortest path "
            "problem for a graph with non-negative edge path costs, producing "
            "a shortest path tree. This algorithm is often used in routing as "
            "a subroutine in other graph algorithms, or in GPS Technology. "
            "I'll add a unicode character here just for completion: Flávio."
        )
        # This output is emulating the result using the 7 class classifier
        self.maxDiff = None
        expected =  {'DATE': [u'1956', u'1959'],
                     'O': [u"Dijkstra 's algorithm , conceived by Dutch computer scientist",
                           u'in',
                           u'and published in',
                           u", -LRB- 1 -RRB- -LRB- 2 -RRB- is a graph search algorithm that solves the single-source shortest path problem for a graph with non-negative edge path costs , producing a shortest path tree . This algorithm is often used in routing as a subroutine in other graph algorithms , or in GPS Technology . I 'll add a unicode character here just for completion : Flávio ."],
                     'PERSON': [u'Edsger Dijkstra']}
        result = StanfordNER().process({'text': text})
        self.assertEqual(result, {'named_entities': expected})
