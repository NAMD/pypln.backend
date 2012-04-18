"""
Configures an interface for accessing files in MongoDb's GridFS
"""
from pymongo import Connection
import gridfs
from gridfs.errors import FileExists
import os
from bson.errors import InvalidStringData



class FS:
    def __init__(self,Database,create = False):
        """
        Sets up a connection to a gridFS on a given database
        if the database does not exist and create=True,
        the Database is also created
        """
        conn = Connection()
        if Database not in conn.database_names():
            if not create:
                raise NameError('Database does not exist. \nCall get_FS with create=True if you want to create it.')
        self.fs = gridfs.GridFS(conn[Database])


    def add_file(self,fname):
        """
        Adds a file to the collection.
        :Parameters:
            - fname: filename
        """
        fn = os.path.split(fname)[1]
        if self.fs.exists(filename=fn):
            #FIXME: this is subject to name collision of different files
            print "file already in GridFS"
            return
        with open(fname, 'r') as f:
            try:
                fid = self.fs.put(f, filename=fn)
            except FileExists:
                print "File %s has already been Processed, skipping."%fn
                fid = None
            except InvalidStringData as err:
                print err,  fn
                fid = None
        return fid
