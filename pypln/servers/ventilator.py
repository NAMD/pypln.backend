#-*- coding:utf-8 -*-
"""
Task ventilator
Binds PUSH socket to tcp://localhost:5557
Sends batch of tasks to workers via that socket
Adapted from 0MQ tutorial ("The Guide")
"""
__docformat__ = "restructuredtext en"

import zmq
import random
import time


context = zmq.Context()
class Ventilator(object):
    """
    Class to push a collection of texts (unicode strings) received down to a population
    of connected workers
    """
    def __init__(self, pushport=5557, pubport=5559, subport=5560):
        # Socket to send messages on

        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:%s"%pushport)
        # Set up a PUB channel to send status information
        self.pub = context.socket(zmq.PUB)
        self.pub.bind("tcp://127.0.0.1:%s"%pubport)
        # Set up a SUB channel to get information about task completion
        self.hear = context.socket(zmq.SUB)
        self.hear.connect("tcp://127.0.0.1:%s"%(subport))
        self.hear.setsockopt(zmq.SUBSCRIBE,"sink-finished") #only hear to msgs starting with "sink-finished"

    def push_load(self,messages=[],  jobid=0):
        """
        Takes a set of messages to pushed to workers
        """
        # The first message is "{'jobid':jobid}" and signals start of batch
        self.sender.send_json({'jobid':jobid})
        for i,msg in enumerate(messages):
            msg['i'] = i
            self.sender.send_json(msg)
            self.pub.send("task-sent:%s|%s"%(i+1,len(messages))) # publishes that it has sent this task

        m = self.hear.recv()
        print "ventilator: ", m
        #TODO: check if there is a better way to check if the queue is empty
