#-*- coding:utf-8 -*-
"""
Created on 28/05/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

import unittest
from pypln.stores.ontology_store import Ontology
import rdflib
import pymongo


class TestOntology(unittest.TestCase):
    def tearDown(self):
        pass

    def test_parse_rdfxml(self):
        O = Ontology('test','testdb','test_ontology')
        O.import_rdfxml("https://bitbucket.org/fccoelho/math-model-ontology/raw/ddcf69f115bc/Modeling%20Ontology/Mathmodels.rdf")
        self.assertIsInstance(O.graph,rdflib.Graph)
    def test_serialize_to_n3(self):
        O = Ontology('test','testdb','test_ontology')
        O.import_rdfxml("https://bitbucket.org/fccoelho/math-model-ontology/raw/ddcf69f115bc/Modeling%20Ontology/Mathmodels.rdf")
        j = O._serialize_to_n3()
        self.assertIsInstance(j,str)

    def test_store_n3(self):
        O = Ontology('test','testdb','test_ontology')
        O.import_rdfxml("https://bitbucket.org/fccoelho/math-model-ontology/raw/ddcf69f115bc/Modeling%20Ontology/Mathmodels.rdf")
        n3 = O._serialize_to_n3()
        O.store()
        coll = pymongo.Connection()['testdb']['test_ontology']
        ont = coll.find_one({'name':'test'})
        self.assertEqual(n3,ont['n3'])


