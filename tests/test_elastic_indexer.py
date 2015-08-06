#-*- coding:utf-8 -*-
u"""
Created on 20/05/15
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'


from mock import patch

from pypln.backend.workers.elastic_indexer import ElasticIndexer
from .utils import TaskTest
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError


class TestIndexer(TaskTest):
    def test_indexing_go_through(self):
        ES = Elasticsearch()
        try:
            ES.indices.delete('test_pypln')
        except NotFoundError:
            pass
        ES.indices.create('test_pypln')
        doc = {
            'index_name': "test_pypln",
            'doc_type': 'document',
            'file_id': 'deadbeef',
            'text': "Om nama Shivaya "*100,
            'contents': 'raw_file_contents',
        }

        doc_id = self.collection.insert(doc)
        ElasticIndexer().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})
        self.assertTrue(refreshed_document['created'])

    @patch('pypln.backend.workers.elastic_indexer.ES')
    def test_regression_indexing_should_not_include_contents(self, ES):
        """
        We should not index the original file contents for two reasons: 1) they
        are not relevant to the search. The `text` attribute should include the
        relevant content and 2) they may be in a binary format that will not be
        serializable.

        See https://github.com/NAMD/pypln.backend/issues/176 for details.
        """
        doc = {
            'index_name': "test_pypln",
            'doc_type': 'document',
            'file_id': 'deadbeef',
            'text': "Om nama Shivaya "*100,
            'contents': 'raw_file_contents',
        }

        doc_id = self.collection.insert(doc)
        ElasticIndexer().delay(doc_id)
        # remove properties that won't be indexed
        index_name = doc.pop("index_name")
        doc_type = doc.pop('doc_type')
        doc.pop('contents')
        doc.pop('_id')
        ES.index.assert_called_with(body=doc, id=doc['file_id'],
                doc_type=doc_type, index=index_name)
