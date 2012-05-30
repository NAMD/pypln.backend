#-*- coding:utf-8 -*-
"""
Created on 28/09/11
by flavio
"""
__author__ = 'flavio'
__docformat__ = "restructuredtext en"


from pypln.stores.mongostore import conn,databases,collection
import zmq
from base import BaseSink
from bson.objectid import ObjectId
from pymongo.errors import OperationFailure
from pypln.logger import make_log

log = make_log(__name__)

context = zmq.Context()

class MongoUpdateSink(BaseSink):
    """
    Sink to update documents in MongoDb
    """

    def start(self):
        """
        Apply update to Documents in any MongoDB collection
        expects a JSON message with the following structure:
        {"database":"mydb","collection":"mycolection","spec":{"_id":"some_id"},"update":{"$set":{"x":2}},"multi":False}
        spec is a dict or SON instance specifying elements which must be present for a document to be updated
        """
        num_tasks = int(self.hear.recv().split("|")[-1])
        # Process tasks forever
        log.info("Sink starting, waiting for %s tasks"%num_tasks)
        total_results = 1
        for i in range(num_tasks):
            msg = self.receiver.recv_json()
            if 'fail' not in msg:
                self.process(msg)
            else:
                self.pub.send("job-failed:")
            total_results += 1

        self.pub.send("sink-finished:%s"%total_results)
        log.info("sink-finished:%s"%total_results)

    def process(self, msg):
        """
        Update documents in the database in batches of size
        self.batchsz
        """
        msg['spec']["_id"] = ObjectId(msg['spec']["_id"])
        if not (msg['database'] in databases and msg['collection'] in conn[msg['database']].collection_names()):
            log.error("Either database %s or collection %s do not exist."%(msg['database'],msg['collection']))
            return
        coll = conn[msg['database']][msg['collection']]
        try:
            coll.update(msg['spec'],msg['update'],multi=msg['multi'])
            log.debug("Updated")
        except TypeError:
            log.error("bad spec or update command.")
        except OperationFailure:
            log.error("failed updating document: {0}".format(msg['_id']))



if __name__== '__main__':
    sink = MongoUpdateSink()
    sink.start()
