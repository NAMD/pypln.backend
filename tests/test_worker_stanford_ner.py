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
        text = (u"Dijkstra's algorithm, conceived by Dutch computer scientist "
            u"Edsger Dijkstra in 1956 and published in 1959,[1][2] is a graph "
            u"search algorithm that solves the single-source shortest path "
            u"problem for a graph with non-negative edge path costs, producing "
            u"a shortest path tree. This algorithm is often used in routing as "
            u"a subroutine in other graph algorithms, or in GPS Technology. "
            u"I'll add a unicode character here just for completion: Flávio."
        )
        self.maxDiff = None
        expected = [('O', 'Dijkstra'), ('O', "'s"), ('O', 'algorithm'),
            ('O', ','), ('O', 'conceived'), ('O', 'by'), ('O', 'Dutch'),
            ('O', 'computer'), ('O', 'scientist'), ('PERSON', 'Edsger'),
            ('PERSON', 'Dijkstra'), ('O', 'in'), ('DATE', '1956'), ('O', 'and'),
            ('O', 'published'), ('O', 'in'), ('DATE', '1959'), ('O', ','),
            ('O', '-LSB-'), ('O', '1'), ('O', '-RSB-'), ('O', '-LSB-'),
            ('O', '2'), ('O', '-RSB-'), ('O', 'is'), ('O', 'a'), ('O', 'graph'),
            ('O', 'search'), ('O', 'algorithm'), ('O', 'that'), ('O', 'solves'),
            ('O', 'the'), ('O', 'single-source'), ('O', 'shortest'),
            ('O', 'path'), ('O', 'problem'), ('O', 'for'), ('O', 'a'),
            ('O', 'graph'), ('O', 'with'), ('O', 'non-negative'), ('O', 'edge'),
            ('O', 'path'), ('O', 'costs'), ('O', ','), ('O', 'producing'),
            ('O', 'a'), ('O', 'shortest'), ('O', 'path'), ('O', 'tree'),
            ('O', '.'), ('O', 'This'), ('O', 'algorithm'), ('O', 'is'),
            ('O', 'often'), ('O', 'used'), ('O', 'in'), ('O', 'routing'),
            ('O', 'as'), ('O', 'a'), ('O', 'subroutine'), ('O', 'in'),
            ('O', 'other'), ('O', 'graph'), ('O', 'algorithms'), ('O', ','),
            ('O', 'or'), ('O', 'in'), ('O', 'GPS'), ('O', 'Technology'),
            ('O', '.'), ('O', 'I'), ('O', "'ll"), ('O', 'add'), ('O', 'a'),
            ('O', 'unicode'), ('O', 'character'), ('O', 'here'), ('O', 'just'),
            ('O', 'for'), ('O', 'completion'), ('O', ':'),
            ('O', 'Fl\xc3\xa1vio'), ('O', '.')]

        result = StanfordNER().process({'text': text})
        self.assertEqual(result, {'named_entities': expected})
