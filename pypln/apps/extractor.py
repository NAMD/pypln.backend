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

def extract(args, vent):
    """Extract texts from file under a given path or on GridFS"""
    pdf_ext_vent = vent
    time.sleep(1)
    if not args.gfs:
        docs = scan_dir(args.path, args.db)
    else:
        docs = scan_gridfs(args.db, args.host)
#    print "number of PDFs ", len(docs['application/pdf'])
    msgs = []
    for k, v in docs.iteritems(): # ['application/pdf']:
        for d in v:
            msgs.append({'database': args.db, 'collection': args.col,
                         'md5': d, 'mimetype': k})
    pdf_ext_vent.push_load(msgs)



def main(args):
    tv = TaskVentilator(Ventilator, DocConverterWorker, MongoInsertSink, 10)
    vent, ws, sink = tv.spawn()
    extract(args, vent)



