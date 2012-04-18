#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This is a script to serialize a query in MongoDB to xml so that it can be indexed by sphinxsearch
XML is output as a stream in order to keep memory usage

the output of this file os compatible with xmlpipe2:
http://sphinxsearch.com/docs/2.0.1/xmlpipe2.html

see mongo2sphinx --help for usage information.

Created on 03/10/11
by flavio
"""
__author__ = 'Flavio Codeço Coelho'


import argparse
from pymongo import Connection
from xml.etree.ElementTree import Element, tostring, SubElement
import sys

SW = sys.stdout #Stream Writer
header = '<?xml version="1.0" encoding="utf-8"?><sphinx:docset>'
schema_head = """<sphinx:schema>
                    <sphinx:attr name="db" type="string"/>
                    <sphinx:attr name="collection" type="string"/>
                    <sphinx:attr name="_id" type="string"/>
                    """

def get_schema_tag(head,fields):
    """
    Returns the schema tag
    """
    for n in fields:
        head += '<sphinx:field name="%s"/>'%n
    return head + "</sphinx:schema>"

def serialize(doc,id):
    """
    Receives raw MongoDB document data and returns xml.
    SphinxSearch demands that each document is identified by
    an unique unsigned integer `id`. We use a counter for this.
    """
    document = Element("sphinx:document", attrib={'id':str(id)})
    for k,v in doc.iteritems():
        if k == '_id':
            SubElement(document,k).text = str(v)
            continue
        SubElement(document,k).text = v
    return tostring(document)
    
    

def query(db, collection, fields,host='127.0.0.1', port=27017):
    """
    Given a mongo db a collection and a list of fields,writes a stream of xml to stdout
    """
    conn = Connection(host,port)
    coll = conn[db][collection]
    cursor = coll.find({},fields=fields)
    locationdic = {'db':db,'collection':collection}
    SW.write(header)
    SW.write(get_schema_tag(schema_head,fields))
    i=1
    for doc in cursor:
        doc.update(locationdic)
        SW.write(serialize(doc,i))
        i+=1
    SW.write("</sphinx:docset>")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Perform a query on mongo db and return it as XML')
    parser.add_argument('--db', '-d',required=True, help="Database")
    parser.add_argument('--col', '-c',required=True, help="Collection")
    parser.add_argument('--host', '-H', type=str, default='127.0.0.1',help="MongoDB Host")
    parser.add_argument('--port', '-p', type=int, default=27017, help="port")
    parser.add_argument('--fields', '-f', required=True,type=str, nargs = "+", help="Fields to be indexed")
    args = parser.parse_args()#    print args, args.prune

    query(db=args.db,collection=args.col,fields=args.fields,host=args.host,port=args.port)
    #TODO: allow the user to specify an unique integer id field to be used in cases where the index needs to be updated if it is not provided, a counter should be used.