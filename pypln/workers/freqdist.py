# coding: utf-8

__meta__ = {'work on': 'document',
            'requires': ['tokens'],
            'provides': ['freqdist'],}

def main(document):
    tokens = document['analysis']['tokens']
    frequency_distribution = {token: tokens.count(token) \
                              for token in set(tokens)}
    fd = frequency_distribution.items()
    fd.sort(lambda x, y: cmp(y[1], x[1]))
    return {'freqdist': fd}
