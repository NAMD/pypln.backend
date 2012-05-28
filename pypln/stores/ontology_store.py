#-*- coding:utf-8 -*-
"""


Created on 28/05/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

import pymongo
import rdflib
import rdfextras
rdfextras.registerplugins()


class Ontology(object):
    """
    Class to store and load ontologies from MOngodb
    """
    def __init__(self,name,db,collection, host="127.0.0.1", port=27017):
        self.name = name
        self.graph = None
        self.connection = pymongo.Connection(host=host,port=port)
        self.collection = self.connection[db][collection]

    def import_rdfxml(self,uri):
        """
        Reads RDF/XML from uri and
        :param uri:
        :return:
        """
        self.graph = rdflib.Graph()
        self.graph.parse(uri,format="application/rdf+xml")
    def store(self):
        """
        Stores ontology in Mongodb. Currently in n3 format
        :return:
        """
        data = self._serialize_to_n3()
        self.collection.insert({'name':self.name,'n3':data})

    def load(self,name):
        """
        Loads Ontology from database and sets self.graph to it
        :param name: Name of the ontology
        :return: None
        """
        data = self.collection.find_one({'name':name})
        self.graph = rdflib.Graph()
        self.graph.parse(data,format = "n3")

    def _serialize_to_n3(self):
        """
        Returns Graph serialized to JSON
        :return: JSON object
        """
        if self.graph:
            return self.graph.serialize(format="n3")
        else:
            return
