# coding: utf-8

from string import punctuation
from nltk.corpus import stopwords
from pypln.util import LANGUAGES


__meta__ = {'from': 'document',
            'requires': ['tokens', 'language'],
            'to': 'document',
            'provides': ['freqdist_with_stopwords',
                         'freqdist_without_stopwords'],}

def main(document):
    tokens = [info.lower() for info in document['tokens']]
    frequency_distribution = {token: tokens.count(token) \
                              for token in set(tokens)}
    fd = frequency_distribution.items()
    fd.sort(lambda x, y: cmp(y[1], x[1]))
    stopwords_list = list(punctuation)
    document_language = LANGUAGES[document['language']].lower()
    if document_language in stopwords.fileids():
        stopwords_list += stopwords.words(document_language)
    fd_without_stopwords = []
    for token, frequency in fd:
        if token not in stopwords_list:
            fd_without_stopwords.append((token, frequency))
    return {'freqdist_with_stopwords': fd,
            'freqdist_without_stopwords': fd_without_stopwords}
