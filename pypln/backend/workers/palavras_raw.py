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

from pypelinin import Worker


PALAVRAS_ENCODING = sys.getfilesystemencoding()
BASE_PARSER = '/opt/palavras/por.pl'
PARSER_MODE = '--dep'

def palavras_installed():
    return os.path.exists(BASE_PARSER)

class PalavrasRaw(Worker):
    requires = ['text', 'language']

    def process(self, document):
        if document['language'] != 'pt' or not palavras_installed():
            return {}

        text = document['text']
        process = subprocess.Popen([BASE_PARSER, PARSER_MODE],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(text.encode(PALAVRAS_ENCODING))

        return {'palavras_raw': stdout}
