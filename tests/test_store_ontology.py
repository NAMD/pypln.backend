#-*- coding:utf-8 -*-

import unittest
import pymongo
import rdflib
from pypln.stores.ontology import Ontology


class TestOntology(unittest.TestCase):
    def test_parse_rdfxml(self):
        O = Ontology('test', 'testdb', 'test_ontology')
        O.import_rdfxml('tests/data/Mathmodels.rdf')
        self.assertIsInstance(O.graph, rdflib.Graph)

    def test_serialize_to_n3(self):
        O = Ontology('test', 'testdb', 'test_ontology')
        O.import_rdfxml('tests/data/Mathmodels.rdf')
        j = O._serialize_to_n3()
        self.assertIsInstance(j, str)

    @unittest.skip('Failing with a lot of output')
    def test_store_n3(self):
        O = Ontology('test', 'testdb', 'test_ontology')
        O.import_rdfxml('tests/data/Mathmodels.rdf')
        n3 = O._serialize_to_n3()
        O.store()
        coll = pymongo.Connection()['testdb']['test_ontology']
        ontology = coll.find_one({'name': 'test'})
        self.assertEqual(n3, ontology['n3'])
