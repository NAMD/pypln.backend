# coding: utf-8

from nltk import word_tokenize


__meta__ = {'work on': 'document',
            'requires': ['text'],
            'provides': ['tokens'],}

def main(document):
    text = document['text']
    return {'tokens': word_tokenize(text)}
