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
    Class to store and load ontologies from Mongodb
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
        self.graph.parse(uri,Format="application/rdf+xml")
    def store(self, Format='n3'):
        """
        Stores ontology in Mongodb. Currently in n3 format
        :param Format: form in which the ontology should be saved
        :return:
        """
        if Format == 'n3':
            data = self._serialize_to_n3()
        else:
            raise TypeError("Format '{}' unsupported".format(Format))
        self.collection.insert({'name':self.name,'data':data,'format':'n3'})

    def load(self,name):
        """
        Loads Ontology from database and sets self.graph to it
        :param name: Name of the ontology
        :return: None
        """
        data = self.collection.find_one({'name':name})
        self.graph = rdflib.Graph()
        self.graph.parse(data,format = data['format'])

    def _serialize_to_n3(self):
        """
        Returns Graph serialized to JSON
        :return: JSON object
        """
        if self.graph:
            return self.graph.serialize(format="n3")
        else:
            return
