#-*- coding:utf-8 -*-
"""
This testing module contains tests of the process methods of workers
These methods should be called directly, with a message, to avoid the need of starting
ventilators and worker processes communicating through ZMQ

Created on 27/02/12
by Flávio Codeço Coelho
"""
__author__ = 'fccoelho'

import unittest
from pypln.workers.highlighter_worker import HighlighterWorker
from pypln.workers.docconv_worker import DocConverterWorker


class TestHighlighterWorker(unittest.TestCase):
    def setUp(self):
        self.W = HighlighterWorker()
    def tearDown(self):
        pass

    def test_single_wordlist(self):
        msg = {'text': ['atirei', 'o', 'pau', 'no', 'gato'],
               'wordlists': {'um': ['pau', 'gato']}
        }
        res = self.W.process(msg)
        self.assertDictEqual(res,{'highlighted_text':['atirei','o','<span class="tagged" title="um"><b>pau</b></span>',
                                                  'no','<span class="tagged" title="um"><b>gato</b></span>']})

    def test_multiple_wordlist(self):
        msg = {'text':['atirei','o','pau','no','gato'],
               'wordlists':{'um':['pau','gato'],'dois':['pau','cachorro']}}
        res = self.W.process(msg)
        self.assertDictEqual(res,{'highlighted_text':['atirei','o','<span class="tagged" title="um,dois"><b>pau</b></span>',
                                                  'no','<span class="tagged" title="um"><b>gato</b></span>']})

class TestPDFWorker(unittest.TestCase):
    def setUp(self):
        self.PC = DocConverterWorker()

    def test_parse_metadata(self):
        md = """Title:          mve_848.dvi
Creator:        dvips 5.83 Copyright 1998 Radical Eye Software
Producer:       Acrobat Distiller 7.0.5 (Windows)
CreationDate:   Tue Feb  9 14:58:46 2010
ModDate:        Tue Feb  9 15:01:34 2010
Tagged:         no
Pages:          8
Encrypted:      no
Page size:      595.276 x 790.866 pts
File size:      644613 bytes
Optimized:      no
PDF version:    1.3
        """
        expected = {'Title':'mve_848.dvi','Creator':'dvips 5.83 Copyright 1998 Radical Eye Software',
                    'Producer':'Acrobat Distiller 7.0.5 (Windows)',
                    'CreationDate':'Tue Feb  9 14:58:46 2010',
                    'ModDate':'Tue Feb  9 15:01:34 2010',
                    'Tagged':'no',
                    'Pages':'8',
                    'Encrypted':'no',
                    'Page size':'595.276 x 790.866 pts',
                    'File size':'644613 bytes',
                    'Optimized':'no',
                    'PDF version':'1.3'
        }
        mdict = self.PC.parse_metadata(md)
        self.assertDictEqual(mdict,expected)
