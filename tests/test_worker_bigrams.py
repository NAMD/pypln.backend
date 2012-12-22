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
from pypln.backend.workers.bigrams import Bigrams
import nltk

bigram_measures = nltk.collocations.BigramAssocMeasures()


class TestBigramWorker(unittest.TestCase):
    def test_bigrams_should_return_correct_score(self):
        tokens = nltk.corpus.genesis.words('english-web.txt')
        bigram_finder = nltk.collocations.BigramCollocationFinder.from_words(tokens)
        expected = bigram_finder.score_ngram(bigram_measures.chi_sq, u'Allon',u'Bacuth')
        bigram_rank = Bigrams().process({'tokens':tokens})['bigram_rank']
        result = bigram_rank[(u'Allon', u'Bacuth')][0]
        self.assertEqual(result, expected)

