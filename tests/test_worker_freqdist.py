# coding: utf-8

import unittest
from pypln.workers import freqdist


class TestFreqDistWorker(unittest.TestCase):
    def test_freqdist_should_return_a_list_of_tuples_with_frequency_distribution(self):
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']
        result = freqdist.main({'tokens': tokens, 'language': 'en'})
        expected_fd =  [('is', 2), ('the', 2), ('blue', 1), ('sun', 1),
                ('sky', 1), (',', 1), ('yellow', 1), ('.', 1)]
        expected = {'freqdist': expected_fd,}
        self.assertEqual(result, expected)
