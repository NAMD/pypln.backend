# coding: utf-8

from nltk import word_tokenize


__meta__ = {'from': 'document',
            'requires': ['text'],
            'to': 'document',
            'provides': ['tokens'],}

def main(document):
    text = document['text']
    result = word_tokenize(text)
    return {'tokens': result}
