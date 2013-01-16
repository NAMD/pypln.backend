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
import gridfs
import nltk
import unittest

from mongodict import MongoDict
from pymongo import Connection

from pypln.backend.mongo_store import MongoDBStore
from pypln.backend.workers.bigrams import Bigrams
from .utils import default_config

bigram_measures = nltk.collocations.BigramAssocMeasures()


class TestBigramWorker(unittest.TestCase):
    def _prepare_store(self):
        self.db_conf = db_conf = default_config['store']
        self.connection = Connection(host=db_conf['host'],
                                     port=db_conf['port'])
        self.connection.drop_database(db_conf['database'])
        self.db = self.connection[db_conf['database']]
        self.monitoring = self.db[db_conf['monitoring_collection']]
        self.gridfs = gridfs.GridFS(self.db, db_conf['gridfs_collection'])
        self.db[db_conf['gridfs_collection'] + '.files'].drop()
        self.db[db_conf['gridfs_collection'] + '.chunks'].drop()
        self.mongodict = MongoDict(host=db_conf['host'], port=db_conf['port'],
                                   database=db_conf['database'],
                                   collection=db_conf['analysis_collection'])
        self.store = MongoDBStore(**db_conf)

    def test_bigrams_should_return_correct_score(self):
        tokens = nltk.corpus.genesis.words('english-web.txt')
        bigram_finder = nltk.collocations.BigramCollocationFinder.from_words(tokens)
        expected = bigram_finder.score_ngram(bigram_measures.chi_sq, u'Allon',u'Bacuth')
        bigram_rank = Bigrams().process({'tokens':tokens})['bigram_rank']
        result = bigram_rank[(u'Allon', u'Bacuth')][0]
        self.assertEqual(result, expected)

    def test_worker_output_should_be_pickleable(self):
        """The workers run under multiprocessing, so their result is
        pickled. This is a regression test."""
        tokens = nltk.corpus.genesis.words('english-web.txt')
        result = Bigrams().process({'tokens':tokens})
        # This should not raise an exception.
        cPickle.dumps(result)

    def test_saving_worker_output_should_work(self):
        """Saving the worker output should work. This is a regression test."""
        self._prepare_store()
        tokens = nltk.corpus.genesis.words('english-web.txt')[:100]
        result = Bigrams().process({'tokens': tokens})
        info = {'data': {'id': 789, '_id': 'eggs'}, 'worker': 'Bigrams',
                'worker_requires': ['tokens'], 'worker_result': result}
        self.store.save(info)
        self.connection.drop_database(self.db)
