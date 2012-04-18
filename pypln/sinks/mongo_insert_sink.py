"""
Sink to save documents in a MongoDb Collection
"""
__author__="flavio"
__date__ ="$13/09/2011 12:03:34$"
__docformat__ = "restructuredtext en"

from pypln.stores.mongostore import collection
import zmq
from base import BaseSink

context = zmq.Context()

class MongoInsertSink(BaseSink):
    """
    Sink to insert documents in MongoDb
    """
    insertlist = []
    batchsz = 3 # Bulk inserts are faster

    def start(self):
        """
        Save msg in a collection in a database in MongoDB
        msg must be a json doc of the form {'database':'...','collection':'','filename':'...','text':'...'}
        or {'fail':1}
        """
        num_tasks = int(self.hear.recv().split("|")[-1])
        # Process tasks forever
        print "Sink starting, waiting for %s tasks"%num_tasks
        total_results = 0
        for i in range(num_tasks):
            msg = self.receiver.recv_json()
            try:
                print total_results+1, msg['filename']
            except KeyError:
                self.flush()
            if 'fail' in msg:
                print "failed conversion"
                self.flush()
            else:
                self.process(msg)
            total_results += 1
            
        
        self.flush() # Always flush before exiting
        self.pub.send("sink-finished:%s"%total_results)
        print "==> sink-finished:%s"%total_results

    def process(self,  msg):
        """
        Write documents in the database and collection in batches of size
        self.batchsz
        """
#        print msg
        coll = collection(msg.pop('database'),msg.pop('collection'))
        self.insertlist.append(msg)
        
        if len(self.insertlist) > self.batchsz:
            print "==> inserting...", 
            coll.insert(self.insertlist)
            self.insertlist = []
    def flush(self):
        print "--> sink flushing"
        if self.insertlist:
            coll.insert(self.insertlist)
            
if __name__=="__main__":
    S=MongoInsertSink()
    S()
