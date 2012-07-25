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
from taw.models import Glossario


urlpatterns = patterns('taw.views', #this is the prefix to the views below:(eg. taw.views.main)
    url(r'^$', "main", name="taw_home"),
    url(r'^corpora/$', 'corpora_page', name="corpora"),
    url(r'^corpus/(?P<corpus_slug>.+)/$','corpus', name="corpus"), # restful corpus access/creation
#    url(r'^corpus/$','corpus', name="corpus"), #for POSTs
    url(r'^createcorpus/$', 'create_corpus'),
    url(r'^search/?', 'search', name='search'),
    url(r'^document/(?P<document_id>.*)', 'document_view', name='document'),
)
