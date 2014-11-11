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
import os

from pypelinin import Worker


BASE_PATH = '/opt/palavras'
NOUNPHRASE_SCRIPT = 'bin/extract_np.pl'

class NounPhrase(Worker):
    """Noun phrase extractor"""
    requires = ['palavras_raw']

    def process(self, document):
        nounphrase_script = os.path.join(BASE_PATH, NOUNPHRASE_SCRIPT)
        process = subprocess.Popen(nounphrase_script, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        palavras_output = document['palavras_raw']
        if isinstance(palavras_output, unicode):
            # we *need* to send a 'str' to the process. Otherwise it's going to try to use ascii.
            palavras_output = palavras_output.encode('utf-8')
        stdout, stderr = process.communicate(palavras_output)

        # We should also return the result as unicode
        phrases = [phrase.strip().decode('utf-8') for phrase in stdout.strip().split('\n')]
        return {'noun_phrases': phrases}
