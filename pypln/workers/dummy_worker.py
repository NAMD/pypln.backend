#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
 Task worker
 Connects PULL socket to tcp://localhost:5557
 Collects workloads from ventilator via that socket
 Connects PUSH socket to tcp://localhost:5558
 Sends results to sink via that socket

 Author: Flávio Codeço Coelho <fccoelho@gmail.com>
"""
import os
import zmq
from base import PushPullWorker, BaseWorker


class DummyWorker(PushPullWorker):
    """
    Dummy worker class which does nothing.
    Currenty just for testing purposes.
    """

    def start(self):
        self.pid = os.getpid() #updating pid in case of fork
        # Process tasks forever
        # print "Worker {} up!".format(self.pid)
        while self.stayalive:
#            msg = self.receiver.recv_json()
#            print msg
            socks = dict(self.poller.poll())
            if self.receiver in socks and socks[self.receiver] == zmq.POLLIN:
                msg = self.receiver.recv_json()
                # print "worker {} received: {}".format(self.pid, msg)
#                if not msg: break # no more tasks left?
                if 'jobid' in msg: # startup message
                    # print "starting job {}".format(msg['jobid'])
                    continue
                self.process(msg)
            if self.sub in socks and socks[self.sub] == zmq.POLLIN:
                msg = self.sub.recv()
                # print '{}: {}'.format(self.pid, msg)
                break
#            print socks

    def process(self,msg):
        self.sender.send_json(msg)

def DummyWorker2():
    """
    Dummy worker function, works better with multiprocessing
    """
    context = zmq.Context()
    pid = os.getpid()
    stayalive = True
    # Set up a SUB channel to get information about task queue completion
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://127.0.0.1:{}".format(5560))
    sub.setsockopt(zmq.SUBSCRIBE, "sink-finished") # only sub to msgs starting with "sink-finished"
    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://127.0.0.1:{}".format(5557))
    # Socket to send messages to
    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://127.0.0.1:{}".format(5558))
    # Initialize poll set to listen on two channels at once
    poller = zmq.Poller()
    poller.register(receiver, zmq.POLLIN)
    poller.register(sub, zmq.POLLIN)
    while stayalive:
#        print "listening..."
#        msg = receiver.recv_json()
        socks = dict(poller.poll(100))
        if receiver in socks and socks[receiver] == zmq.POLLIN:
            msg = receiver.recv_json()
            # print '{}: {}'.format(pid, msg)
            if not msg: break # no more tasks left?
            if 'jobid' in msg: # startup message
                # print "starting job {}".format(msg['jobid'])
                continue
        if sub in socks and socks[sub] == zmq.POLLIN:
            msg = sub.recv()
            # print '{}: {}'.format(pid, msg)
            break


if __name__=="__main__":
    worker = DummyWorker()
    worker()
