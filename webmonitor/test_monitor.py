#-*- coding:utf-8 -*-
u"""
Created on 13/06/12
by fccoelho
license: GPL V3 or Later
"""

import unittest
import monitor
from pymongo import Connection

monitor.Db = Connection()['pypln']

__docformat__ = 'restructuredtext en'

class TestMonitor(unittest.TestCase):
    def test_fetching_xminutes_from_db(self):
        self.assertGreater(len(monitor.fetch_x_minutes(10)),0)
