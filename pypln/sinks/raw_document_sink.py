#-*- coding:utf-8 -*-
"""
 Document sink
 Binds PULL socket to tcp://localhost:5558
 Collects text from workers via that socket and stores in the Document database

 Author: Flávio Codeço Coelho <fccoelho@gmail.com>
"""
import sys
import time
import zmq
from base import BaseSink
from stores.document import  Documentos
# ******** WARNING! : UNTESTED ****************
context = zmq.Context()
class RawDocumentSink(BaseSink):
    """
    this worker expects to receive a Document in raw text format (encoded in utf-8)
    and store it in a MongoDb database for further processing
    """
    def start(self):
        """
        starts receiving
        """
        num_tasks = int(self.hear.recv().split("|")[-1])

        # Process tasks forever
        total_results = 0
        while 1:
            s = self.receiver.recv_json(encoding='utf-8')
            self.process(s)
            total_results +=1
            if total_results == numtasks:
                self.monitor.send("sink-finished:%s"%total_results)
                break
            
    def process(self, msg):
            """
            msg: JSON containing document text and descriptors
            """
            Documentos.rawtext.insert(msg)

        
if __name__=="__main__":
    S=RawDocumentSink()
    S.start()
