#-*- coding:utf-8 -*-
u"""
Created on 13/06/12
by fccoelho
license: GPL V3 or Later
"""

import unittest
import monitor
from pymongo import Connection
import json

monitor.Db = Connection()['pypln']

__docformat__ = 'restructuredtext en'

class TestMonitor(unittest.TestCase):
    def test_fetching_xminutes_from_db(self):
        self.assertGreater(len(monitor.fetch_x_minutes(10)),0)
    def test_getting_stats(self):
        self.assertIsInstance(json.loads(monitor.get_cluster_stats()),dict)
    def test_fetch_last_jobs(self):
        self.assertIsInstance(monitor.fetch_last_jobs(),dict)
        self.assertIsInstance(monitor.fetch_last_jobs().values(),list)

