#-*- coding:utf-8 -*-
"""
Mimetype detection worker
"""

import mimetypes
import zmq
from base import PushPullWorker

context = zmq.Context()

class MimeWorker(PushPullWorker):
    def start(self):
        # Process tasks forever
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
        Tries to detect the mimetype based on filename or
        """
        mt = mimetypes.guess_type(msg)
        #TODO: figure out a way to report a failure
        self.sender.send_unicode(mt[0],encoding='utf-8')

if __name__=="__main__":
    # this is run when worker is spawned directly from the console
    W=MimeWorker()
    W.start()
