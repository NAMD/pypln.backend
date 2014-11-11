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

PALAVRAS_ENCODING = 'utf-8'
WORD_CLASSES = {
                u'N': u'Nouns',
                u'PROP': u'Proper nouns',
                u'SPEC': u'Specifiers',
                u'DET': u'Determiners',
                u'PERS': u'Personal pronouns',
                u'ADJ': u'Adjectives',
                u'ADV': u'Adverbs',
                u'V': u'Verbs',
                u'NUM': u'Numerals',
                u'PRP': u'Preposition',
                u'KS': u'Subordinating conjunctions',
                u'KC': u'Coordinationg conjunctions',
                u'IN': u'Interjections',
                u'EC': u'Hyphen-separated prefix',
                u'BL': u'Blank Line',
                u'ES': u'End of Sentence',
                u'NW': u'Non Word',
}


def pos(document):
    if 'palavras_raw' not in document:
        return u'', []

    palavras_output = document['palavras_raw']
    if not isinstance(palavras_output, unicode):
        palavras_output = palavras_output.decode(PALAVRAS_ENCODING)
    tagged_text = []
    for line in palavras_output.split(u'\n'):
        line = line.strip()
        #print(line)
        if line.isspace() or line == u'':
            continue
        elif line.startswith(u'<'):
            continue
        elif line.startswith(u'$'):
            non_word = line.split()[0][1:]
            if non_word.isdigit():
                non_word_tag = u'NUM'
            else:
                non_word_tag = non_word
            tagged_text.append((non_word, non_word_tag))
        elif len(line.split(u'\t')) < 2: # Discard malformed lines
            continue
        else:
            info = line.split(u'\t')
            final = u'\t'.join(info[1:]).split()
            word = info[0].strip()
            syntatic_semantic_tags = final[1:]
            tags = filter(lambda x: x in WORD_CLASSES, syntatic_semantic_tags)
            if tags:
                pos_tag = tags[0]
                tagged_text.append((word, pos_tag))
    return 'pt-palavras', tagged_text
