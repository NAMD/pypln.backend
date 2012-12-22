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

import nltk
from collections import defaultdict

from nltk.collocations import BigramCollocationFinder
from pypelinin import Worker


class Bigrams(Worker):
    """Create a NLTK bigram finder and return a table in JSON format"""
    requires = ['tokens']


    def process(self, document):
        #todo: support filtering by stopwords
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        metrics = ['chi_sq',
               'dice',
               'jaccard',
               'likelihood_ratio',
               'mi_like',
               'phi_sq',
               'pmi',
               'poisson_stirling',
               'raw_freq',
               'student_t']
        bigram_finder = BigramCollocationFinder.from_words(document['tokens'])
        br = defaultdict(lambda :[])
        for m in metrics:
            for res in bigram_finder.score_ngrams(getattr(bigram_measures,m)):
                br[res[0]].append(res[1])
        return {'metrics':metrics,'bigram_rank': br}
