# coding: utf-8

from pypelinin import Worker

from nltk import word_tokenize, sent_tokenize


class Tokenizer(Worker):
    requires = ['text']

    def process(self, document):
        text = document['text']
        tokens = word_tokenize(text)
        sentences = [word_tokenize(sent) for sent in sent_tokenize(text)]
        return {'tokens': tokens, 'sentences': sentences}
