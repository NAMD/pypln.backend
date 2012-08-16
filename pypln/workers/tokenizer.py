# coding: utf-8

from nltk import word_tokenize, sent_tokenize


__meta__ = {'from': 'document',
            'requires': ['text'],
            'to': 'document',
            'provides': ['tokens', 'sentences'],}

def main(document):
    text = document['text']
    tokens = word_tokenize(text)
    sentences = []
    for sentence in sent_tokenize(text):
        sentences.append(word_tokenize(sentence))
    return {'tokens': tokens, 'sentences': sentences}
