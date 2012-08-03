#-*- coding:utf-8 -*-
u"""
PyPLN API - This module contains API definitions based on Django-tastypie library
Created on 25/07/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

from tastypie.resources import ModelResource
from pypln.stores.mongo import MongoDBStore
#TODO: change initialization below to use global configuration
MS = MongoDBStore(**{'host':'127.0.0.1','port':27017,
                     'database': 'pypln',
                     'corpora_collection': 'corpora',
                     'document_collection': 'documents',
                     'analysis_collection': 'analysis',
                     'gridfs_collection': 'files',
                     'monitoring_collection': 'monitoring'})
Corpus = MS.Corpus
Document = MS.Document


class CorpusResource(ModelResource):
    class Meta:
        queryset = Corpus.all
        resource_name = 'corpus'

class DocumentResource(ModelResource):
    class Meta:
        queryset = Document.all
