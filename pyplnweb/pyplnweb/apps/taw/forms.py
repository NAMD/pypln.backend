#-*- coding:utf-8 -*-
"""
Created on 21/03/12
by fccoelho
"""
__author__ = 'fccoelho'

from django import forms
from taw.models import Corpus

class CorpusForm(forms.Form):
    name = forms.CharField(max_length=64,min_length=3, required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    private = forms.BooleanField(required=True, initial=False)

    def check_name(self):
        """
        Check name availability in the document store
        :return:
        """
        data = self.cleaned_data['name']
        #TODO: stubify and look it up in the Documento Store
        if data in []:
            raise forms.ValidationError("This name is taken. please try a new one")
        return data

class DocumentForm(forms.Form):
    file = forms.FileField(required=True)

