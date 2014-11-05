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

from pypelinin import Worker

import nltk
from nltk.collocations import TrigramCollocationFinder
from collections import defaultdict



class Trigrams(Worker):
    """Create a NLTK trigram finder and returns a table in JSON format"""
    requires = ['tokens']

    def process(self, document):
        trigram_measures = nltk.collocations.TrigramAssocMeasures()
        metrics = ['chi_sq',
                   'jaccard',
                   'likelihood_ratio',
                   'mi_like',
                   'pmi',
                   'poisson_stirling',
                   'raw_freq',
                   'student_t']
        trigram_finder = TrigramCollocationFinder.from_words(document['tokens'])
        tr = defaultdict(lambda: [])
        for m in metrics:
            for res in trigram_finder.score_ngrams(getattr(trigram_measures,m)):
                tr[res[0]].append(res[1])

        return {'trigram_rank': tr, 'metrics':metrics}
