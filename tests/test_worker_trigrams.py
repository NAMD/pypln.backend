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
from pypln.backend.workers.trigrams import Trigrams
import nltk
import cPickle

trigram_measures = nltk.collocations.TrigramAssocMeasures()


class TestTrigramWorker(unittest.TestCase):
    def test_Trigrams_should_return_correct_score_(self):
        tokens = nltk.corpus.genesis.words('english-web.txt')
        trigram_finder = nltk.collocations.TrigramCollocationFinder.from_words(tokens)
        expected = trigram_finder.score_ngram(trigram_measures.chi_sq, u'olive', u'leaf',u'plucked')
        trigram_rank = Trigrams().process({'tokens':tokens})['trigram_rank']
        result = trigram_rank[(u'olive', u'leaf',u'plucked')][0]
        self.assertEqual(result, expected)

