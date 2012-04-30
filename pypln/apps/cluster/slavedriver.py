#!/usr/bin/env python
#-*- coding:utf-8 -*-
u"""
Created on 27/04/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

import zmq
import sys, atexit
from pypln.servers import baseapp
import logging
from zmq.core.error import ZMQError
from logger import make_log

log = make_log("Slavedriver")



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
        self.context = zmq.Context(1)
        self.pullconf = self.context.socket(zmq.REQ)
        self.pullconf.connect("tcp://%s"%(self.master_uri))
        self.pullconf.send('slavedriver')
        try:
            self.localconf = self.pullconf.recv_json()
            self.pullsock = self.context.socket(zmq.PULL)
            self.pullsock.connect("tcp://%s:%s"%(self.localconf['master_ip'],self.localconf['pullport']))
            log.info('Slavedriver started on %s')
        except ZMQError:
            log.error("Could Not fetch configuration from Manager!")
            self.pullconf.close()
            self.pullsock.close()
            self.context.term()
            sys.exit()



    def run(self):
        """
        Infinite loop listening  form messages from master node and passing them to an app.
        :return:
        """
        try:
            while True:
                msg = self.pullsock.recv_json()
                print "Slavedriver got ",msg
        except (KeyboardInterrupt,SystemExit):
            self.pullconf.close()
            self.pullsock.close()
            self.context.term()

if __name__=='__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    SD = SlaveDriver(master_uri=sys.argv[1])
    SD.run()



