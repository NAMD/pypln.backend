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

from pypln.backend.workers import Tokenizer
from utils import TaskTest


class TestTokenizerWorker(TaskTest):
    def test_tokenizer_should_receive_text_and_return_tokens(self):
        self.document['text'] = 'The sky is blue, the sun is yellow. This is another sentence.'

        expected_tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
            'yellow', '.', 'This', 'is', 'another', 'sentence', '.']
        expected_sentences = [['The', 'sky', 'is', 'blue', ',', 'the', 'sun',
            'is', 'yellow', '.'], ['This', 'is', 'another', 'sentence', '.']]

        Tokenizer().delay(self.fake_id)

        tokens = self.document['tokens']
        sentences = self.document['sentences']

        self.assertEqual(tokens, expected_tokens)
        self.assertEqual(sentences, expected_sentences)
