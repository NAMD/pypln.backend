# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN.
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
