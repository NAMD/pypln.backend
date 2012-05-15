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
__docformat__ = "restructuredtext en"

import os
import sys,argparse
from collections import defaultdict
import mimetypes
from multiprocessing import Process
from subprocess import Popen
from pypln.servers.ventilator import Ventilator
from pypln.servers.baseapp import TaskVentilator
from pypln.stores.filestor import FS
from pypln.workers.pdfconv_worker import PDFConverterWorker
from pypln.sinks.mongo_insert_sink import MongoInsertSink
from pymongo import Connection
from pypln.workers.pdfconv_worker import PDFConverterWorker
import time

def scan_dir(path, db, recurse=False):
    """
    Scans a directory, adds files to the GridFS and returns
    dictionary of files by mimetype
    """
    fs = FS(db,True)
    docdict = defaultdict(lambda:[])
    for p, dirs, files in os.walk(path):
        if not recurse:
            dirs = []
        for f in files:
            mt = mimetypes.guess_type(f)[0]
            #classify documents by mimetype
            try:
                fullpath = os.path.join(os.getcwd(),os.path.join(p, f).decode('utf8'))
            except UnicodeDecodeError:
                print "skipping: ",f
                continue
            fid = fs.add_file(fullpath)
            if fid != None:
                doc = fs.fs.get(fid)
                docdict[mt].append(doc.md5)
    return docdict

def scan_gridfs(db,host):
    """
    scans gridfs under a given database and returns
    a dictionary of files by mimetype
    """
    #TODO: maybe it's better to identify files by ID in both these scan functions.
    docdict = defaultdict(lambda:[])
    files = Connection('127.0.0.1')[db].fs.files
    fs = FS(db,True)
    cursor = files.find()
    for f in cursor:
        mt = mimetypes.guess_type(f)['filename']#classify documents by mimetype
        doc = fs.get(f['_id'])
        docdict[mt].append(doc.md5)
    return docdict
    
def setup_workers(nw=5):
    """
    Start the worker processes
    """
    WP = [Process(target=PDFConverterWorker()) for i in range(nw)]
    [p.start() for p in WP]
    #WP = [Popen(['python', '../pypln/workers/pdfconv_worker.py'], stdout=None) for i in range(nw)]
    return WP
    
def setup_sink():
    """
    Start ns sink process(es)
    """
    SP = [Process(target=MongoInsertSink())]
    SP[0].start()
    #SP = [Popen(['python', '../pypln/sinks/mongo_insert_sink.py'], stdout=None)]
    return SP

def extract(path,nw=10):
    #TODO: Currently broken. Implement a generic text extractor worker which is mimetype aware
    pdf_ext_vent = Ventilator(pushport=5557, pubport=5559, subport=5560)
    time.sleep(1)
    docs = scan_dir(path, args.db)
    print "number of PDFs ",len(docs['application/pdf'])
    msgs = []
    for v in docs['application/pdf']:
        msgs.append({'database':args.db,'collection':args.col,'md5':v})
    pdf_ext_vent.push_load(msgs)

def directory(d):
    """
    checks if path is a directory
    """
    if os.path.isdir(d):
        pass
    else:
        msg = "%s is not a directory" % d
        raise argparse.ArgumentTypeError(msg)
    return d
            
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Scans a directory tree or gridfs distributed file system looking for files to convert to text')
    #group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-H', '--host', default='127.0.0.1', help='Host ip of the MongoDB server.')
    parser.add_argument('-d', '--db', required=True, help="Database in which to deposit the texts")
    parser.add_argument('-c', '--col', required=True, help="Collection in which to deposit the texts")
    parser.add_argument('-g','--gfs', help=" Scan griGridFS under db. Overrides path")
    parser.add_argument( 'path', metavar='p', type=directory, help="Path of directory to scan for documents")

    args = parser.parse_args()

    if len(sys.argv) >1:
        p = sys.argv[1]
    else:
        p= "/home/flavio/Documentos/Reprints/"

    ports = {'ventilator':(5557,5559,5559), # pushport,pubport,subport
             'worker':(5564,5561,5563),          # pushport,pullport,subport
             'sink':(5564,5563,5562)   # pullport,pubport,subport
    }

    tv = TaskVentilator(Ventilator,PDFConverterWorker,MongoInsertSink,10,ports)
    sinks = setup_sink()
    workers = setup_workers(8)
    extract(args.path,8)


