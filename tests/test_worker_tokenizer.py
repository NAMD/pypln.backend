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

import unittest
from pypln.backend.workers import tokenizer

from mongodict import MongoDict


class TestTokenizerWorker(unittest.TestCase):
    def test_tokenizer_should_receive_text_and_return_tokens(self):
        fake_id = '1234'
        text = 'The sky is blue, the sun is yellow. This is another sentence.'
        expected_tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
            'yellow', '.', 'This', 'is', 'another', 'sentence', '.']
        expected_sentences = [['The', 'sky', 'is', 'blue', ',', 'the', 'sun',
            'is', 'yellow', '.'], ['This', 'is', 'another', 'sentence', '.']]

        document = {'text': text}
        db = MongoDict(database="pypln_backend_test")
        # This is just preparing the expected input in the database
        db['id:{}:text'.format(fake_id)] = text

        # Apply the task synchronously for tests
        tokenizer.apply(fake_id)

        db = MongoDict(database="pypln_backend_test")

        tokens = db['id:{}:tokens'.format(fake_id)]
        sentences = db['id:{}:sentences'.format(fake_id)]

        self.assertEqual(tokens, expected_tokens)
        self.assertEqual(sentences, expected_sentences)
