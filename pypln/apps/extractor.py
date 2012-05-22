#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
New Document processor

This app scans a directory and submits new/changed documents to the
preprocessing pipeline
Which will perform, in order:
* mimetype detection
* encoding detection
* text extraction and conversion if necessary
* Storage of extracted text in database
"""

__docformat__ = "reStructuredText en"

import os
import sys, argparse
from collections import defaultdict
import mimetypes
from pypln.servers.ventilator import Ventilator
from pypln.servers.baseapp import TaskVentilator
from pypln.stores.filestor import FS
from pypln.sinks.mongo_insert_sink import MongoInsertSink
from pymongo import Connection
from pypln.workers.docconv_worker import DocConverterWorker
import time


def scan_dir(path, db, recurse=False):
    """
    Scans a directory, adds files to the GridFS and returns
    dictionary of files by mimetype
    """
#    print "==> scanning file system..."
    fs = FS(db, True)
    docdict = defaultdict(lambda: [])
    for p, dirs, files in os.walk(path):
        if not recurse:
            dirs = []
        for f in files:
            mt = mimetypes.guess_type(f)[0]
            # classify documents by mimetype
            try:
                fullpath = os.path.join(os.getcwd(), os.path.join(p, f).decode('utf8'))
            except UnicodeDecodeError:
                # print "skipping: ",f
                continue
            fid = fs.add_file(fullpath)
            if fid != None:
                doc = fs.fs.get(fid)
                docdict[mt].append(doc.md5)
            #TODO: maybe handle the case when the files are already on gridfs but have not been extracted yet
    return docdict

def scan_gridfs(db, host):
    """
    scans gridfs under a given database and returns
    a dictionary of files by mimetype
    :param db: Database where to look for gridfs
    :param host: Host where to find Mongodb
    :return: Dictionary of documents by mimetype
    """
    #TODO: maybe it's better to identify files by ID in both these scan functions.
    docdict = defaultdict(lambda: [])
    files = Connection(host)[db].fs.files
    fs = FS(db)
    cursor = files.find()
    for f in cursor:
        mt = mimetypes.guess_type(f['filename'])[0] # classify documents by mimetype
        doc = fs.fs.get(f['_id'])
        docdict[mt].append(doc.md5)
    return docdict

def extract(path, vent):
    """Extract texts from file under a given path or on GridFS"""
    pdf_ext_vent = vent
    time.sleep(1)
    if not args.gfs:
        docs = scan_dir(path, args.db)
    else:
        docs = scan_gridfs(args.db, args.host)
#    print "number of PDFs ", len(docs['application/pdf'])
    msgs = []
    for k, v in docs.iteritems(): # ['application/pdf']:
        for d in v:
            msgs.append({'database': args.db, 'collection': args.col,
                         'md5': d, 'mimetype': k})
    pdf_ext_vent.push_load(msgs)

def directory(d):
    """Check if path is a directory"""
    if os.path.isdir(d):
        return d
    else:
        raise argparse.ArgumentTypeError('{} is not a directory'.format(d))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scans a directory tree or gridfs distributed file system looking for files to convert to text')
    #group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-H', '--host', default='127.0.0.1', help='Host ip of the MongoDB server.')
    parser.add_argument('-d', '--db', required=True, help='Database in which to deposit the texts')
    parser.add_argument('-c', '--col', required=True, help="Collection in which to deposit the texts")
    parser.add_argument('-g', '--gfs', action='store_true',help="Scan griGridFS under db. ignores path")
    parser.add_argument('path', metavar='p', type=directory, help="Path of directory to scan for documents")
    args = parser.parse_args()

    tv = TaskVentilator(Ventilator, DocConverterWorker, MongoInsertSink, 10)
    vent, ws, sink = tv.spawn()
#    sinks = setup_sink()
#    workers = setup_workers(8)
    extract(args.path, vent)
