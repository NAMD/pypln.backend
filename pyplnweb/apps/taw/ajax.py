#-*- coding:utf-8 -*-
"""
Ajax calls to be user by dajaxice
Created on 12/03/12
by fccoelho
"""
__author__ = 'fccoelho'

from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
import pymongo as PM
from django.conf import settings
from taw.models import Corpus, Document

# Initialize mongo connection
connection = PM.Connection(settings.MONGODB, settings.MONGODB_PORT)

@dajaxice_register
def my_test(request):
    return simplejson.dumps({'message':'Hello World, it works!'})

@dajaxice_register
def get_doc_list(request, data):
    """
    Fetch sample list of documents from MongoDB for preview
    """
#    print data
    collection, db = data
    docs = connection[db][collection].find(limit=10)
    return simplejson.dumps({'message':str(docs),'db':db,'collection':collection})

@dajaxice_register
def add_doclist_to_corpus(request,docs=[],keys=[],corpus='',db='',coll=''):
    """
    Add selected documents to a corpus, creating one if necessary
    """
    id_index = keys.index('_id')
    print corpus
    cp = Corpus.objects.filter(title=corpus)
    print "corpus id: ",cp
    for d in docs[0]:
        print d
        doc = Document.objects.get(mongoid=d[id_index])
        print "read ", doc
        if not doc:
            doc = Document(mongoid=d[id_index],database=db,collection=coll)
            doc.save()
            print "created: ",
        print doc
        cp.docs.add(doc)
        print "added ", doc
    cp.save()
    print docs, keys, corpus,db,coll
    return simplejson.dumps({'message':'worked'})
