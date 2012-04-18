"""
Define a Mongo Document database for storing raw text documents and metadata
"""
from pymongo import Connection
from pymongo import ASCENDING, DESCENDING

conn = Connection('127.0.0.1', 27017)

databases = conn.database_names()

def collection(database, collection):
    """
    Returns a collection in a mongodb database
    """
    return conn[database][collection]

