#-*- coding:utf-8 -*-
"""
Created on 15/12/11
by fccoelho
"""
__author__ = 'fccoelho'

from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic import ListView
from taw.models import Document, Corpus, Glossario



urlpatterns = patterns('taw.views', #this is the prefix to the views below:e.g. taw.views.main
    url(r"^$","main"),
    url(r"^documents/$",ListView.as_view(model=Document,)),
    url(r"^corpora/$", ListView.as_view(model=Corpus,)),
    url(r'^collections/$','collection_browse'),
    url(r'^collections/(?P<dbname>\w+)/(?P<collname>\w+)/$','document_browse'),
    url(r'^createcorpus/$','create_corpus'),
    )