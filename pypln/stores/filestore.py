# coding: utf-8
"""
Configure an interface for accessing files in MongoDB's GridFS
"""

import os
from hashlib import md5
from logging import Logger, StreamHandler, Formatter
from sys import stdout
from pymongo import Connection
from gridfs import GridFS
from gridfs.errors import FileExists
from bson.errors import InvalidStringData


class FS(object):
    def __init__(self, database, host='127.0.0.1', port=27017, usr=None,
                 pw=None, create=False, logger=None):
        """
        Sets up a connection to a gridFS on a given database
        if the database does not exist and create=True,
        the Database is also created
        :param Database: Database on which to look for GridFS
        :param host: Host of the MongoDB
        :param port: Port of MongoDB
        :param usr: user authorized for the connection
        :param pw: password for the authorized user
        :param create: whether to create a file storage if it doesn't exist
        """
        self.conn = Connection(host=host, port=port)
        if database not in self.conn.database_names():
            if not create:
                raise NameError('Database does not exist (if you want to '
                                'create, use create=True')
            else:
                self.db = self.conn[database]
                if usr and pw:
                    self.db.add_user(usr, pw)
        self.db = self.conn[database]
        if usr and pw:
            self.db.authenticate(usr, pw)
        self.fs = GridFS(self.db)
        if logger is None:
            logger = Logger('filestore')
            handler = StreamHandler(stdout)
            formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        self.logger = logger

    def _rename(self, fn):
        """
        Get a filename to rename (try variations to find an available name)
        :return: filename
        """
        i = 0
        pos = fn.find('.',-5) #finds the dot before the extension
        while self.fs.exists(filename=fn):
            fn = fn.strip(str(i))
            i += 1
            fn = fn[:pos]+"_"+str(i)+fn[pos:]
        return fn

    def add_file(self, fname):
        """
        Add a file to the collection
        :Parameters:
            - fname: filename
        """
        fn = os.path.split(fname)[1]
        if self.fs.exists(filename=fn):
            # Check md5 to see if the files are really the same
            ef = self.fs.get_version(filename=fn)
            with open(fname, 'r') as f:
                filemd5 = md5(f.read()).hexdigest()
            if ef.md5 == filemd5:
                self.logger.warning('File {} has already been stored, '
                                    'skipping.'.format(fn))
                return
            else:
                fn_new = self._rename(fn)
                self.logger.warning('Name collision. Renaming {0} to {1}'\
                            .format(fn, fn_new))
        else:
            fn_new = fn

        with open(fname, 'r') as f:
            try:
                fid = self.fs.put(f, filename=fn_new)
            except FileExists:
                self.logger.warning('File {} has already been processed, '
                                    'skipping.'.format(fn))
                fid = None
            except InvalidStringData as err:
                self.logger.error('Invalid string data for file {0}'.format(fn))
                fid = None
        return fid

    def drop(self):
        """ Drop the file storage """
        self.db.drop_collection('fs')
