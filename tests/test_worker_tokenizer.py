# coding: utf-8

import unittest
from pypln.workers import tokenizer


class TestTokenizerWorker(unittest.TestCase):
    def test_tokenizer_should_receive_text_and_return_tokens(self):
        text = 'The sky is blue, the sun is yellow.'
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']
        result = tokenizer.main({'text': text})
        self.assertEqual(result, {'tokens': tokens})

