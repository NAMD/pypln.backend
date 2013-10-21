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

PALAVRAS_PATH = '/opt/palavras/'

class Lemmatizer(Worker):
    """Lemmatizer"""

    requires = ['palavras_raw']

    def process(self, document):

        lines = document['palavras_raw'].split('\n')
        lemmas = []
        for line in lines:
            if line.startswith('$'): # punctuation
                lemmas.append(line.split('#')[0].split('$')[1].strip())
            else: # other tokens
                data = line.split('[')
                if len(data) > 1: # if it is a real token
                    lemmas.append(line.split('[')[1].split(']')[0])

        return {'lemmas': lemmas}
