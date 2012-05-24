#-*- coding:utf-8 -*-
"""
Created on 21/03/12
by fccoelho
"""
__author__ = 'fccoelho'

from django import forms
from taw.models import Corpus

class CorpusForm(forms.ModelForm):
    class Meta:
        model = Corpus
        fields = ('title','description')
  