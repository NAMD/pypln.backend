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

import nltk

from pypln.backend.workers.bigrams import Bigrams
from utils import TaskTest

bigram_measures = nltk.collocations.BigramAssocMeasures()


class TestBigramWorker(TaskTest):
    def test_bigrams_should_return_correct_score(self):
        # We need this list comprehension because we need to save the word list
        # in mongo (thus, it needs to be json serializable). Also, a list is
        # what will be available to the worker in real situations.
        tokens = [w for w in
                nltk.corpus.genesis.words('english-web.txt')]

        doc_id = self.collection.insert({'tokens': tokens})
        bigram_finder = nltk.collocations.BigramCollocationFinder.from_words(tokens)
        expected = bigram_finder.score_ngram(bigram_measures.chi_sq, u',', u'which')

        Bigrams().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})
        bigram_rank = refreshed_document['bigram_rank']
        result = bigram_rank[0][1][0]
        self.assertEqual(result, expected)
