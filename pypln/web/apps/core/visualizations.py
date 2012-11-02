# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

from string import punctuation
from django.utils.translation import ugettext as _
from nltk.corpus import stopwords
from utils import TAGSET, COMMON_TAGS, LANGUAGES


def _token_frequency_histogram(data):
    from collections import Counter

    freqdist = data['freqdist']
    values = Counter()
    for key, value in freqdist:
        values[value] += 1
    data['values'] = [list(x) for x in values.most_common()]
    del data['freqdist']
    data['momentum_1'] = '{:.2f}'.format(data['momentum_1'])
    data['momentum_2'] = '{:.2f}'.format(data['momentum_2'])
    data['momentum_3'] = '{:.2f}'.format(data['momentum_3'])
    data['momentum_4'] = '{:.2f}'.format(data['momentum_4'])
    return data

def _pos_highlighter(data):
    pos = []
    if data['pos'] is not None:
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
    stopwords_list = list(punctuation)
    document_language = LANGUAGES[data['language']].lower()
    if document_language in stopwords.fileids():
        stopwords_list += stopwords.words(document_language)
    data['freqdist'] = [[repr(x[0])[2:-1], x[1]] for x in data['freqdist'] \
                                                 if x[0] not in stopwords_list]
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
             'requires': set(['freqdist', 'momentum_1', 'momentum_2',
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
            'requires': set(['freqdist', 'language']),
            'process': _wordcloud,
        },
}
