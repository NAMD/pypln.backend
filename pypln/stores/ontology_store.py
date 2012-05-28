#-*- coding:utf-8 -*-
"""


Created on 28/05/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'


import rdflib
import rdfextras
rdfextras.registerplugins()


class Ontology(object):
    """
    Class to store and load ontologies from MOngodb
    """
    def __init__(self):
        self.graph = None
    def import_rdfxml(self,uri):
        """
        Reads RDF/XML from uri and
        :param uri:
        :return:
        """
        self.graph = rdflib.Graph()
        self.graph.parse(uri,format="application/rdf+xml")
    def _store(self):
        pass
    def _serialize_to_n3(self):
        """
        Returns Graph serialized to JSON
        :return: JSON object
        """
        if self.graph:
            return self.graph.serialize(format="n3")
        else:
            return
