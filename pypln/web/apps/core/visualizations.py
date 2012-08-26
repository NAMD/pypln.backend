# coding: utf-8

from django.utils.translation import ugettext as _
from pypln.util import TAGSET, COMMON_TAGS


def _token_frequency_histogram(data):
    from collections import Counter

    freqdist = data['freqdist_without_stopwords']
    values = Counter()
    for key, value in freqdist:
        values[value] += 1
    data['values'] = [list(x) for x in values.most_common()]
    del data['freqdist_without_stopwords']
    data['momentum_1'] = '{:.2f}'.format(data['momentum_1'])
    data['momentum_2'] = '{:.2f}'.format(data['momentum_2'])
    data['momentum_3'] = '{:.2f}'.format(data['momentum_3'])
    data['momentum_4'] = '{:.2f}'.format(data['momentum_4'])
    return data

def _pos_highlighter(data):
    pos = []
    for item in data['pos']:
        pos.append({'slug': TAGSET[item[1]]['slug'], 'token': item[0]})
    return {'pos': pos, 'tagset': TAGSET, 'most_common': COMMON_TAGS[:20]}

def _statistics(data):
    data['repertoire'] = '{:.2f}'.format(data['repertoire'] * 100)
    data['average_sentence_repertoire'] = \
            '{:.2f}'.format(data['average_sentence_repertoire'] * 100)
    data['average_sentence_length'] = '{:.2f}'.format(data['average_sentence_length'])
    data['number_of_tokens'] = len(data['tokens'])
    data['number_of_unique_tokens'] = len(set(data['tokens']))
    sentences = []
    for sentence in data['sentences']:
        sentences.append(' '.join(sentence))
    data['number_of_sentences'] = len(sentences)
    data['number_of_unique_sentences'] = len(set(sentences))
    data['percentual_tokens'] = '{:.2f}'.format(100 * data['number_of_unique_tokens'] / data['number_of_tokens'])
    data['percentual_sentences'] = '{:.2f}'.format(100 * data['number_of_unique_sentences'] / data['number_of_sentences'])
    return data

def _wordcloud(data):
    data['freqdist_without_stopwords'] = [[repr(x[0])[2:-1], x[1]] for x in data['freqdist_without_stopwords']]
    return data

VISUALIZATIONS = {
        'text': {
            'label': _('Plain text'),
            'requires': set(['text']),
        },
        'pos-highlighter': {
            'label': _('Part-of-speech'),
            'requires': set(['pos', 'tokens']),
            'process': _pos_highlighter,
        },
        'token-frequency-histogram': {
             'label': _('Token frequency histogram'),
             'requires': set(['freqdist_without_stopwords', 'momentum_1', 'momentum_2',
                              'momentum_3', 'momentum_4']),
             'process': _token_frequency_histogram,
        },
        'statistics': {
            'label': _('Statistics'),
            'requires': set(['tokens', 'sentences', 'repertoire',
                             'average_sentence_repertoire',
                             'average_sentence_length']),
            'process': _statistics,
        },
        'word-cloud': {
            'label': _('Word cloud'),
            'requires': set(['freqdist_without_stopwords']),
            'process': _wordcloud,
        },
}
