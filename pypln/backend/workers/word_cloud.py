# coding: utf-8
#
# Copyright 2014 NAMD-EMAP-FGV
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

import base64
from StringIO import StringIO

import numpy
from wordcloud import make_wordcloud

from pypelinin import Worker

class WordCloud(Worker):
    requires = ['freqdist']

    def process(self, document):
        fdist = document['freqdist']
        words = numpy.array([t[0] for t in fdist])
        counts = numpy.array([t[1] for t in fdist])
        wordcloud_img = make_wordcloud(words, counts,
                font_path='/usr/share/fonts/TTF/DejaVuSans.ttf')
        fd = StringIO()
        wordcloud_img.save(fd, format="PNG")
        fd.seek(0)
        result = {'wordcloud': base64.b64encode(fd.read())}
        fd.close()

        return result
