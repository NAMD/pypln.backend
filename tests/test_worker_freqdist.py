# coding: utf-8

import unittest
from pypln.workers import freqdist


class TestFreqDistWorker(unittest.TestCase):
    def test_freqdist_should_return_a_list_of_tuples_with_frequency_distribution(self):
        tokens = [('The', 'DT', 0), ('sky', 'NN', 4), ('is', 'VBZ', 8),
                  ('blue', 'JJ', 11), (',', ',', 15), ('the', 'DT', 17),
                  ('sun', 'NN', 21), ('is', 'VBZ', 25), ('yellow', 'JJ', 28),
                  ('.', '.', 34)]
        result = freqdist.main({'tokens': tokens})
        expected = {'freqdist': [('is', 2), ('the', 2), ('blue', 1),
                                 ('sun', 1), ('sky', 1), (',', 1),
                                 ('yellow', 1), ('.', 1)]}
        self.assertEqual(result, expected)
