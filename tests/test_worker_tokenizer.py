# coding: utf-8

import unittest
from pypln.backend.workers import Tokenizer


class TestTokenizerWorker(unittest.TestCase):
    def test_tokenizer_should_receive_text_and_return_tokens(self):
        text = 'The sky is blue, the sun is yellow. This is another sentence.'
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow.', 'This', 'is', 'another', 'sentence', '.']
        sentences = [['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                      'yellow', '.'], ['This', 'is', 'another', 'sentence',
                                       '.']]
        result = Tokenizer().process({'text': text})
        self.assertEqual(result['tokens'], tokens)
        self.assertEqual(result['sentences'], sentences)
