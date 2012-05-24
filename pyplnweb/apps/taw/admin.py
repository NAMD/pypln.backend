#-*- coding:utf-8 -*-
"""
Created on 22/03/12
by fccoelho
"""
__author__ = 'fccoelho'

from django.contrib import admin
from taw.models import Document,Corpus, Glossario

class DocumentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Document, DocumentAdmin)

class CorpusAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created'
    pass
admin.site.register(Corpus, CorpusAdmin)

class GlossarioAdmin(admin.ModelAdmin):
    pass
admin.site.register(Glossario,GlossarioAdmin)