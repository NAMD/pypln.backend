#-*- coding:utf-8 -*-
u"""
Created on 20/05/15
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'


from pypln.backend.workers.elastic_indexer import ElasticIndexer
from .utils import TaskTest
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError


class TestIndexer(TaskTest):
    def test_indexing_go_through(self):
        ES = Elasticsearch()
        try:
            ES.indices.delete('test')
        except NotFoundError:
            pass
        ES.indices.create('test')
        doc = {
            'index_name': "test",
            'doc_type': 'document',
            'pypln_id': 1,
            'text': "Om nama Shivaya "*100
        }

        self.document.update(doc)
        ElasticIndexer().delay(self.fake_id)
        assert self.document['created']  # must be True
