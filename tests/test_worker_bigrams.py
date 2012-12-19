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

import cPickle
import unittest

import nltk

from pypln.backend.workers.bigrams import Bigrams


class TestBigramWorker(unittest.TestCase):
    def test_bigrams_should_return_10_best_bigrams_in_this_order(self):
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        tokens = nltk.corpus.genesis.words('english-web.txt')
        worker_result = Bigrams().process({'tokens': tokens})
        finder = cPickle.loads(worker_result['bigram_finder'])

        expected = [(u'Allon', u'Bacuth'),
                    (u'Ashteroth', u'Karnaim'),
                    (u'Ben', u'Ammi'),
                    (u'En', u'Mishpat'),
                    (u'Jegar', u'Sahadutha'),
                    (u'Salt', u'Sea'),
                    (u'Whoever', u'sheds'),
                    (u'appoint', u'overseers'),
                    (u'aromatic', u'resin'),
                    (u'cutting', u'instrument')]
        result = finder.nbest(bigram_measures.pmi, 10)
        self.assertEqual(result, expected)
