# coding: utf-8

import unittest
from pypln.workers import pos


class TestPosWorker(unittest.TestCase):
    def test_pos_should_return_a_list_of_tuples_with_token_classification_and_offset(self):
        text = 'The sky is blue, the sun is yellow.'
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']
        expected = [('The', 'DT', 0), ('sky', 'NN', 4), ('is', 'VBZ', 8),
                   ('blue', 'JJ', 11), (',', ',', 15), ('the', 'DT', 17),
                   ('sun', 'NN', 21), ('is', 'VBZ', 25), ('yellow', 'JJ', 28),
                   ('.', '.', 34)]
        result = pos.main({'text': text, 'tokens': tokens,
                           'language': 'english'})
        self.assertEqual(result, {'pos': expected})

