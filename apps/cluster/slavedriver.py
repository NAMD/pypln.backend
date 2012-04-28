#!/usr/bin/env python
#-*- coding:utf-8 -*-
u"""
Created on 27/04/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

import zmq
import sys
from pypln.servers import baseapp
import logging
log = logging.getLogger(__name__)



class SlaveDriver(object):
    """
    Class to manage work on slave nodes
    """
    def __init__(self, master_uri):
        """
        SlaveDriver
        :param opts: dictionary with parameters from pypln.conf
        :return:
        """
        self.master_uri = master_uri
        context = zmq.Context(1)
        self.pullconf = context.socket(zmq.REQ)
        self.pullconf.connect("tcp://%s"%(self.master_uri))
        self.pullconf.send('slavedriver')
        self.localconf = self.pullconf.recv()
        self.pullsock = context.socket(zmq.PULL)
        self.pullsock.connect("tcp://%s:%s"%(self.localconf['masterip'],self.localconf['pullport']))


        log.info('Slavedriver started on %s')

    def run(self):
        """
        Infinite loop listening  form messages from master node and passing them to an app.
        :return:
        """
        while True:
            msg = self.pullsock.recv_json()
            print msg
if __name__=='__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    SlaveDriver(master_uri=sys.argv[1])



