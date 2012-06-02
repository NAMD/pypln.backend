#-*- coding:utf-8 -*-

__docformat__ = 'restructuredtext en'

import pymongo
import rdflib
import rdfextras


rdfextras.registerplugins()

class Ontology(object):
    """ Store and load ontologies from Mongodb """

    def __init__(self, name, db, collection, host='127.0.0.1', port=27017):
        self.name = name
        self.graph = None
        self.connection = pymongo.Connection(host=host, port=port)
        self.collection = self.connection[db][collection]

    def import_rdfxml(self, uri):
        """ Read RDF/XML from ``uri`` """
        self.graph = rdflib.Graph()
        self.graph.parse(uri, format='application/rdf+xml')

    def store(self):
        """ Store ontology in MongoDB (currently in n3 format) """
        data = self._serialize_to_n3()
        self.collection.insert({'name': self.name, 'n3': data})

    def load(self, name):
        """ Load ontology from database and set self.graph to it """
        data = self.collection.find_one({'name': name})
        self.graph = rdflib.Graph()
        self.graph.parse(data, format='n3')

    def _serialize_to_n3(self):
        """ Return graph serialized to JSON """
        if self.graph:
            return self.graph.serialize(format='n3')
        else:
            return None
