"""
Base classes for sinks
"""

__author__="flavio"
__date__ ="$19/07/2011 12:03:34$"

import zmq
import os
#context = zmq.Context()

class BaseSink(object):
    def __init__(self, pullport=5558, pubport=5560,  subport=5559):
        self.pullport = pullport
        self.pubport = pubport
        self.subport = subport
        self.stayalive = True

    def __call__(self):
        context = zmq.Context()
        self.pid = os.getpid()
        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://127.0.0.1:%s"%self.pullport)
        # Set up a PUB channel to send status information
        self.pub = context.socket(zmq.PUB)
        self.pub.bind("tcp://127.0.0.1:%s"%(self.pubport))
        # Set up a SUB channel to get information about remaining results
        self.hear = context.socket(zmq.SUB)
        self.hear.connect("tcp://127.0.0.1:%s"%self.subport)
        self.hear.setsockopt(zmq.SUBSCRIBE,"task-sent:") #only hear to msgs starting with "task-sent:"
        self.start()

    def stop(self):
        self.stayalive = False

    def start(self):
        """
        Starts listening for results
        Subclasses may overload this method
        """
        while self.stayalive:
            msg = self.receiver.recv_json()
            self.process(msg)
            
    def process(self,msg):
        """
        this method must be overloaded by subclasses
        """
        raise NotImplementedError

if __name__ == "__main__":
    pass
