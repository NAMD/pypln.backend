"""
Configures an interface for accessing files in MongoDb's GridFS
"""
from pymongo import Connection
import gridfs
from gridfs.errors import FileExists
import os
from bson.errors import InvalidStringData
from pypln.logger import make_log
from hashlib import md5

# Setting up the logger
log = make_log(__name__)

#TODO: write tests for this class

class FS:
    def __init__(self,database,host='127.0.0.1', port=27017, usr=None, pw=None, create = False):
        """
        Sets up a connection to a gridFS on a given database
        if the database does not exist and create=True,
        the Database is also created
        :param Database: Database on which to look for GridFS
        :param host: Host of the Mongodb
        :param port: Port of Mongodb
        :param usr: user authorized for the connection
        :param pw: password for the authorized user
        :param create: whether to create a file storage if it doesn't exist
        """
        self.conn = Connection(host=host,port=port)
        if database not in self.conn.database_names():
            if not create:
                raise NameError('Database does not exist. \nCall get_FS with create=True if you want to create it.')
            else:
                self.db = self.conn[database]
                if usr and pw:
                    self.db.add_user(usr,pw)
        self.db = self.conn[database]
        if usr and pw:
            self.db.authenticate(usr,pw)
        self.fs = gridfs.GridFS(self.db)


    def _rename(self,fn):
        """
        Gets a file name to rename and tries various extensions to find an available name
        :return: filename
        """
        i = 0
        while self.fs.exists(filename=fn):
            fn = fn.strip(str(i))
            i += 1
            fn += str(i)
        return fn

    def add_file(self,fname):
        """
        Adds a file to the collection.
        :Parameters:
            - fname: filename
        """
        fn = os.path.split(fname)[1]
        if self.fs.exists(filename=fn):
            # Check md5 to see if the files are really the same
            ef = self.fs.get_version(filename=fn)
            with open(fname, 'r') as f:
                filemd5 = md5(f.read())
            if ef.md5 == filemd5:
                log.warning("File %s has already been Stored, skipping."%fn)
                return
            else:
                fn_new  = self._rename(fn)
                log.warning("Name collision. Renaming {0} to {1}".format(fn,fn_new))
        else:
            fn_new = fn

        with open(fname, 'r') as f:
            try:
                fid = self.fs.put(f, filename=fn_new)
            except FileExists:
                log.warning("File %s has already been Processed, skipping."%fn)
                fid = None
            except InvalidStringData as err:
                log.error("Invalid string data for file {0}".format(fn))
                fid = None
        return fid

    def drop(self):
        """
        Drops the file storage
        :return:
        """
        self.db.drop_collection('fs')
