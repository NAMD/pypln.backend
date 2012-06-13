#-*- coding:utf-8 -*-

import unittest
from gridfs import GridFS
from pypln.stores import filestore


class TestFileStore(unittest.TestCase):
    def test_create_connect(self):
        fs = filestore.FS('test', usr='usu', pw='pass', create=True)
        self.assertIsInstance(fs.fs, GridFS)
        fs.drop()
