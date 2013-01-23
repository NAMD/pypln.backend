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

from pypelinin import Worker

import en_nltk
import pt_palavras


MAPPING = {
           'en': en_nltk.pos,
           'pt': pt_palavras.pos,
}
if not pt_palavras.palavras_installed():
    del(MAPPING['pt'])

def put_offset(text, tagged_text):
    result = []
    position = 0
    for token, classification in tagged_text:
        token_position = text.find(token, position)
        result.append((token, classification, token_position))
        position = token_position + len(token) - 1
    return result

class POS(Worker):
    requires = ['text', 'tokens', 'language']

    def process(self, document):
        tagged_text_with_offset = None
        tagset = None
        language = document['language']
        if language in MAPPING:
            tagset, tagged_text = MAPPING[language](document['tokens'])
            tagged_text_with_offset = put_offset(document['text'], tagged_text)
        return {'pos': tagged_text_with_offset, 'tagset': tagset}
