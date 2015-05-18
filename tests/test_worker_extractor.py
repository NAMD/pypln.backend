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
from textwrap import dedent
from pypln.backend.workers import Extractor
from utils import TaskTest

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

class TestExtractorWorker(TaskTest):
    def test_extraction_from_text_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'test.txt')
        self.document.update({'filename': filename,
            'contents': open(filename).read()})
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['text'], expected)
        self.assertEqual(self.document['file_metadata'], {})
        self.assertEqual(self.document['mimetype'], 'text/plain')

    def test_extraction_from_html_file(self):
        expected = "This is a test file. I'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'test.html')
        data = {'filename': filename, 'contents': open(filename).read()}
        self.document.update(data)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['text'], expected)
        self.assertEqual(self.document['file_metadata'], {})
        self.assertEqual(self.document['mimetype'], 'text/html')

    def test_extraction_from_pdf_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'test.pdf')
        data = {'filename': filename, 'contents': open(filename).read()}
        self.document.update(data)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['text'], expected)
        # Check that the expected metadata is a subset of what
        # our Extractor found (it may have found more details
        # depending on the toolset used to extract metadata)
        metadata_expected = {
                'Author':         'Álvaro Justen',
                'Creator':        'Writer',
                'Producer':       'LibreOffice 3.5',
                'CreationDate':   'Fri Jun  1 17:07:57 2012',
                'Tagged':         'no',
                'Pages':          '1',
                'Encrypted':      'no',
                'Page size':      '612 x 792 pts (letter)',
                'Optimized':      'no',
                'PDF version':    '1.4',
        }
        metadata_expected_set = set(metadata_expected.iteritems())
        metadata = self.document['file_metadata']
        metadata_set = set(metadata.iteritems())
        diff_set = metadata_expected_set - metadata_set
        self.assertTrue(metadata_expected_set.issubset(metadata_set),
                        ("Extracted metadata is not a subset of the expected metadata. "
                         "Items missing or with different values: {}").format(
                         u", ".join(unicode(item) for item in diff_set)))
        self.assertEqual(self.document['mimetype'], 'application/pdf')

    def test_extraction_from_html(self):
        contents = dedent('''
        <html>
          <head>
            <title>Testing</title>
            <script type="text/javascript">this must not appear</script>
            <style type="text/css">this must not appear [2]</style>
          </head>
          <body>
            python test1
            <br>
            test2
            <table>
              <tr><td>spam</td></tr>
              <tr><td>eggs</td></tr>
              <tr><td>ham</td></tr>
            </table>
            test3
            <div>test4</div>test5
            <span>test6</span>test7
            <h1>bla1</h1> bla2
          </body>
        </html>
        ''')
        data = {'filename': 'test.html', 'contents': contents}
        self.document.update(data)
        result = Extractor().delay(self.fake_id)
        expected = dedent('''
            Testing

            python test1
            test2

            spam
            eggs
            ham

            test3
            test4
            test5 test6 test7

            bla1

            bla2''').strip()
        self.assertEqual(self.document['text'], expected)
        self.assertEqual(self.document['mimetype'], 'text/html')

    def test_language_detection_pt(self):
        text_pt = 'Esse texto foi escrito por Álvaro em Português.'
        data_pt = {'filename': 'text-pt.txt', 'contents': text_pt}
        self.document.update(data_pt)
        Extractor().delay(self.fake_id).get()
        self.assertEqual(self.document['language'], 'pt')

    def test_language_detection_es(self):
        text_es = 'Este texto ha sido escrito en Español por Álvaro.'
        data_es = {'filename': 'text-es.txt', 'contents': text_es}
        self.document.update(data_es)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['language'], 'es')

    def test_language_detection_en(self):
        text_en = 'This text was written by Álvaro in English.'
        data_en = {'filename': 'text-en.txt', 'contents': text_en}
        self.document.update(data_en)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['language'], 'en')

    def test_unescape_html_entities(self):
        expected = (u"This text has html <entities>. Álvaro asked me to make"
                     " sure it also has non ascii chars.")
        filename = os.path.join(DATA_DIR, 'test_html_entities.txt')
        data = {'filename': filename, 'contents': open(filename).read()}
        self.document.update(data)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['text'], expected)

    def test_should_detect_encoding_and_return_a_unicode_object(self):
        expected = u"Flávio"
        filename = os.path.join(DATA_DIR, 'test_iso-8859-1.txt')
        data = {'filename': filename, 'contents': open(filename).read()}
        self.document.update(data)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['text'], expected)
        self.assertEqual(type(self.document['text']), unicode)

    def test_should_guess_mimetype_for_file_without_extension(self):
        contents = "This is a test file. I'm testing PyPLN extractor worker!"
        filename = os.path.join(DATA_DIR, 'text_file')
        data = {'filename': filename, 'contents': contents}
        self.document.update(data)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['mimetype'], 'text/plain')

    def test_unknown_mimetype_should_be_flagged(self):
        filename = os.path.join(DATA_DIR, 'random_file')
        # we can't put the expected text content here, so we'll just make sure
        # it's equal to the input content, since
        contents = open(filename).read()
        data = {'filename': filename, 'contents': contents}
        self.document.update(data)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['mimetype'], 'unknown')
        self.assertEqual(self.document['text'], "")
        self.assertEqual(self.document['language'], "")
        self.assertEqual(self.document['file_metadata'], {})

    def test_unknown_encoding_should_be_ignored(self):
        filename = os.path.join(DATA_DIR, 'encoding_unknown_to_libmagic.txt')
        expected = u"This file has a weird byte (\x96) that makes it impossible for libmagic to recognize it's encoding."
        data = {'filename': filename, 'contents': open(filename).read()}
        self.document.update(data)
        Extractor().delay(self.fake_id)
        self.assertEqual(self.document['text'], expected)
        self.assertEqual(self.document['file_metadata'], {})
        self.assertEqual(self.document['language'], 'en')
