"""
Base classes for workers
"""
import sys
import zmq
import time
import os

#context = zmq.Context()

#TODO: move here common methods and attributes of workers
#TODO: get port numbers from package level PORTS variable
class BaseWorker(object):
    def __init__(self, subport=5560):
        self.subport = 5560
        self.stayalive = True

    def __call__(self):
        """
        worker instances can be started by direct calling
        This is for compatibility with multiprocessing.Process
        """
        # Initialization had to be moved into __call__ for compatibility with multiprocessing.
        # This way the sockets are created in the child process, when the worked is activated
        self.context = zmq.Context()
        self.pid = os.getpid()
        # Set up a SUB channel to get information about task queue completion
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://127.0.0.1:%s"%(self.subport))
        self.sub.setsockopt(zmq.SUBSCRIBE,"sink-finished") #only sub to msgs starting with "sink-finished"

        self.start()

    def stop(self):
        self.stayalive = False
        
    def start(self):
        """
        Starts listening on receiver port for messages
        this method maybe overloaded by specific workers
        Runs forever until msg is received on the self.sub channel
        """
        # Process tasks forever
        print self.pid,  " starting"
        msgproc = 0
        while self.stayalive:
            socks = dict(self.poller.poll())
            if self.receiver in socks and socks[self.receiver] == zmq.POLLIN:
                msg = self.receiver.recv_json()
                if 'jobid' in msg: # startup message
                    print "starting job %s"%msg['jobid']
                    self.sender.send_json({'fail':1})
                else:
                    self.process(msg)
                msgproc += 1
            if self.sub in socks and socks[self.sub] == zmq.POLLIN:
                msg = self.sub.recv()
                print self.pid, " Done after processing %s messages"%msgproc
                break
            
    def process(self,msg):
        """
        This method must be overloaded by derived workers
        """
        raise NotImplementedError
    
class PushPullWorker(BaseWorker):
    """
    Base class for worker which user the push-pull protocol
    """
    def __init__(self, pullport=5557, pushport=5558, subport=5560):
        """
        All workers of this type must define three sockets for communication:
        :param pullport: Port through which incoming jobs arrive from ventilator
        :param pushport: Port through which results are forwarded to sink
        :param subport: Port to listen for control messages
        """
        self.pullport = pullport
        self.pushport = pushport
        self.subport = subport
        # call base class constructor
        BaseWorker.__init__(self,subport=self.subport)



        
    def __call__(self, *args, **kwargs):
        """
        worker instances can be started by direct calling
        This is for compatibility with multiprocessing.Process
        """
        self.context = zmq.Context()
        self.pid = os.getpid()
        # Set up a SUB channel to get information about task queue completion
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://127.0.0.1:%s"%(self.subport))
        self.sub.setsockopt(zmq.SUBSCRIBE,"sink-finished") #only sub to msgs starting with "sink-finished"
        # Socket to receive messages on
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect("tcp://127.0.0.1:%s"%self.pullport)
        # Socket to send messages to
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.connect("tcp://127.0.0.1:%s"%self.pushport)
        # Initialize poll set to listen on two channels at once
        self.poller = zmq.Poller()
        self.poller.register(self.receiver, zmq.POLLIN)
        self.poller.register(self.sub, zmq.POLLIN)
        # start listening
        self.start()

    def start(self):
        """
        Starts listening on receiver port for messages
        this method maybe overloaded by specific workers
        """
        
        while self.stayalive:
            socks = dict(self.poller.poll())
            if self.receiver in socks and socks[self.receiver] == zmq.POLLIN:
                msg = self.receiver.recv_json()
                if 'jobid' in msg: # startup message
                    continue
                self.process(msg)
            if self.sub in socks and socks[self.sub] == zmq.POLLIN:
                msg = self.sub.recv()
                print msg
                break


    
    def process(self,msg):
        """
        This method must be overloaded by derived workers
        """
        # Simple progress indicator for the viewer
        sys.stdout.write(',')
        sys.stdout.flush()

        # Send results to sink
        self.sender.send_json(msg)
