# coding: utf-8

from pypelinin import Worker


class FreqDist(Worker):
    requires = ['tokens', 'language']

    def process(self, document):
        tokens = [info.lower() for info in document['tokens']]
        frequency_distribution = {token: tokens.count(token) \
                                  for token in set(tokens)}
        fd = frequency_distribution.items()
        fd.sort(lambda x, y: cmp(y[1], x[1]))
        return {'freqdist': fd}
