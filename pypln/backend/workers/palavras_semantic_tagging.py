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


import subprocess
from pypelinin import Worker
import re

PALAVRAS_PATH = '/opt/palavras/'
SEMANTIC_TAGS = {}

exp = re.compile('<([a-zA-Z]*)>')

class SemanticTagger(Worker):
    """Semantic Tagger"""
    requires = ['palavras_raw']

    def process(self, document):

        process = subprocess.Popen(PALAVRAS_PATH+'por.pl', stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(document['palavras_raw'])
        linhas = stdout.split('\n')
        tags = []
        for l in linhas:
            matches = exp.findall(l.strip())
            for m in matches:
                tagged = False
                for k, v in SEMANTIC_TAGS.iteritems():
                    if m in v:
                        tags.append(k)
                        #tags.append(m)
                        tagged = True
                if not tagged:
                    tags.append('0')

        return {'semantic_tags': tags}


