# coding: utf-8

import unittest
from pypln.workers import extractor


def clear_text(text):
    text = text.replace('\n', '')
    text = text.strip()
    while '  ' in text:
        text = text.replace('  ', ' ')
    text = text.replace(' . ', '.')
    return text

original_text = "This is a test file.I'm testing PyPLN extractor worker!"

class TestExtractor(unittest.TestCase):
    def test_extraction_from_text_file(self):
        filename = 'tests/data/test.txt'
        data = {'name': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        text = clear_text(result['text'])
        metadata = result['metadata']
        self.assertEquals(original_text, text)
        self.assertEquals(metadata, None)

    def test_extraction_from_html_file(self):
        filename = 'tests/data/test.html'
        data = {'name': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        text = clear_text(result['text'])
        metadata = result['metadata']
        self.assertEquals(original_text, text)
        self.assertEquals(metadata, None)

    def test_extraction_from_pdf_file(self):
        filename = 'tests/data/test.pdf'
        data = {'name': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        text = clear_text(result['text'])
        metadata = result['metadata']
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
        self.assertEquals(original_text, text)
        self.assertEquals(metadata, metadata_expected)
