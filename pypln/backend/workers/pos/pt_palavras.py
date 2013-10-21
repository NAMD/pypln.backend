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

import os
import subprocess
import sys

PALAVRAS_ENCODING = sys.getfilesystemencoding()
WORD_CLASSES = {
                'N': 'Nouns',
                'PROP': 'Proper nouns',
                'SPEC': 'Specifiers',
                'DET': 'Determiners',
                'PERS': 'Personal pronouns',
                'ADJ': 'Adjectives',
                'ADV': 'Adverbs',
                'V': 'Verbs',
                'NUM': 'Numerals',
                'PRP': 'Preposition',
                'KS': 'Subordinating conjunctions',
                'KC': 'Coordinationg conjunctions',
                'IN': 'Interjections',
                'EC': 'Hyphen-separated prefix',
                'BL': 'Blank Line',
                'ES': 'End of Sentence',
                'NW': 'Non Word',
}


def pos(document):
    if 'palavras_raw' not in document:
        return '', []

    palavras_output = document['palavras_raw']
    tagged_text = []
    for line in palavras_output.split('\n'):
        line = line.strip().decode(PALAVRAS_ENCODING)
        if line.isspace() or line == '':
            continue
        elif line.startswith('<'):
            continue
        elif line.startswith('$'):
            non_word = line.split()[0][1:]
            if non_word.isdigit():
                non_word_tag = 'NUM'
            else:
                non_word_tag = non_word
            tagged_text.append((non_word, non_word_tag))
        elif len(line.split('\t')) < 2: # Discard malformed lines
            continue
        else:
            info = line.split('\t')
            final = '\t'.join(info[1:]).split()
            word = info[0].strip()
            syntatic_semantic_tags = final[1:]
            tags = filter(lambda x: x in WORD_CLASSES, syntatic_semantic_tags)
            if tags:
                pos_tag = tags[0]
                tagged_text.append((word, pos_tag))
    return 'pt-palavras', tagged_text
