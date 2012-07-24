#-*- coding:utf-8 -*-
"""
Created on 22/03/12
by fccoelho
"""
__author__ = 'fccoelho'

from django.contrib import admin
from taw.models import Glossario



class GlossarioAdmin(admin.ModelAdmin):
    pass
admin.site.register(Glossario,GlossarioAdmin)
