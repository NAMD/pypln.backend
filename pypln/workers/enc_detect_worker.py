#-*- coding:utf-8 -*-
"""
Character encoding detection worker
"""

import zmq
from base import PushPullWorker
import chardet


context = zmq.Context()

class EncodingWorker(PushPullWorker):
    def start(self):
        """
        Process tasks forever while waits for finish message.
        """
        while True:
            socks = dict(self.poller.poll())
            if self.receiver in socks and socks[self.receiver] == zmq.POLLIN:
                msg = self.receiver.recv_unicode(encoding='utf-8')
                self.process(msg)
            if self.hear in socks and socks[self.hear] == zmq.POLLIN:
                msg = self.hear.recv()
                # print msg
                break

    def process(self,msg):
        """
        Tries to detect the encoding of a text
        """
        enc = chardet.detect(msg)

        if enc['confidence']>=0.8:
            self.sender.send_unicode(enc[0],encoding='utf-8')
        else:
            pass

if __name__=="__main__":
    # this is run when worker is spawned directly from the console
    worker = EncodingWorker()
    worker.start()
