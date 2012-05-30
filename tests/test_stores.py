#-*- coding:utf-8 -*-
"""
Created on 30/05/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

import unittest
from pypln.stores import filestor
import gridfs

class TestFileStore(unittest.TestCase):
    def test_create_connect(self):
        fs = filestor.FS("test",usr='usu',pw='pass',create=True)
        self.assertIsInstance(fs.fs,gridfs.GridFS)
        fs.drop()


