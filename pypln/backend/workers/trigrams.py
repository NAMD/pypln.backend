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
from nltk.collocations import TrigramCollocationFinder
from collections import defaultdict
from pypln.backend.celery_task import PyPLNTask



class Trigrams(PyPLNTask):
    """Create a NLTK trigram finder and returns a table in JSON format"""

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
                # We cannot store the trigram as a tuple (mongo keys need to be
                # strings). We decided to join tokens using spaces since a
                # space will never be in a token.
                key = u' '.join(res[0])
                # Mongo cannot have `.` or `$` in key names. Unfortunatelly
                # this means we need to replace them with placeholders.
                key = key.replace(u'$', u'\dollarsign')
                key = key.replace(u'.', u'\dot')
                tr[key].append(res[1])

        return {'trigram_rank': tr, 'metrics':metrics}
