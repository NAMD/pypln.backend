#-*- coding:utf-8 -*-
"""
 Task sink
 Binds PULL socket to tcp://localhost:5558
 Collects results from workers via that socket

 Author: Flávio Codeço Coelho <fccoelho@gmail.com>
"""
import os
import time
import zmq
from base import BaseSink

context = zmq.Context()
class DummySink(BaseSink):
    def start(self):
        """
        starts results receiving
        """
        self.pid = os.getpid()
        print "Sink %s starting..."%self.pid
        num_tasks = int(self.hear.recv().split("|")[-1])

        # Process tasks forever
        total_results = 0
        while self.stayalive:
            s = self.receiver.recv_json()
            total_results += 1
            print "#",
            if total_results == num_tasks:
                for i in xrange(10):
                    self.pub.send("sink-finished:%s"%total_results)
                    time.sleep(.1)
                print "==> sink-finished:%s"%total_results
                break

        
if __name__=="__main__":
    S=DummySink()
    S()
