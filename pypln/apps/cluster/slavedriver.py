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
import subprocess
import sys
from multiprocessing import cpu_count
import re
from pypln.servers import baseapp
import logging
from zmq.core.error import ZMQError
from logger import make_log
import os
import psutil

log = make_log("Slavedriver")

class SlaveDriver(object):
    """
    Class to manage work on slave nodes
    """
    def __init__(self, master_uri, run=True):
        """
        SlaveDriver
        :param opts: dictionary with parameters from pypln.conf
        :return:
        """
        self.master_uri = master_uri
        self.pid = os.getpid()
        self.ipaddress = get_ipv4_address()
        self.context = zmq.Context(1)
        self.pullconf = self.context.socket(zmq.REQ)
        self.pullconf.connect("tcp://%s"%(self.master_uri))
#        self.pullconf.send("slavedriver")
        self.pullconf.send_json({"type":"slavedriver","pid":self.pid,"ip":self.ipaddress,
                                 "system":{"cpus":cpu_count(),"memory":psutil.phymem_usage()}})
        try:
            self.localconf = self.pullconf.recv_json()
            self.pullsock = self.context.socket(zmq.PULL)
            self.pullsock.connect("tcp://%s:%s"%(self.localconf['master_ip'],self.localconf['pullport']))
            self.pubsock = self.context.socket(zmq.PUB)
            self.pubsock.bind("tcp://*:%s"%(self.localconf['pubport']))
            log.debug('Slavedriver %s started on %s'%(self.pid,self.ipaddress))
        except ZMQError:
            log.error("Could Not fetch configuration from Manager!")
            self.pullconf.close()
            self.pullsock.close()
            self.context.term()
            sys.exit()
        except KeyError:
            log.error("Defective slavedriver configuration file (missing key)")
            print self.localconf

        # Setup the poller
        self.poller = zmq.Poller()
        self.poller.register(self.pullsock, zmq.POLLIN)
        self.poller.register(self.pubsock,zmq.POLLOUT)
        if run:
            self._run()



    def _run(self):
        """
        Infinite loop listening  form messages from master node and passing them to an app.
        :return:
        """
        log.info("%s at %s  Starting listening cycle..."%(self.pid,self.ipaddress))
        try:
            while True:
                socks = dict(self.poller.poll())
                if self.pullsock in socks and socks[self.pullsock] == zmq.POLLIN:
                    print "Slavedriver listening... ",msg
                    msg = self.pullsock.recv_json(zmq.NOBLOCK)
                    print "Slavedriver got ",msg
                    log.info("Slavedriver got %s"%msg)
                if self.pubsock in socks and socks[self.pubsock] == zmq.POLLOUT:
                    log.info("Slavedriver %s at %s publishing status."%(self.pid,self.ipaddress))
                    self.pubsock.send_json({'pid':self.pid,'status':"Alive"})
        except ZMQError:
            log.info("No message to receive...")
        except (KeyboardInterrupt,SystemExit):
            self.pullconf.close()
            self.pullsock.close()
            self.pubsock.close()
            self.context.term()
            sys.exit()

def get_ipv4_address():
    """
    Returns IPv4 address(es) of current machine.
    :return:
    """
    p = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
    ifc_resp = p.communicate()
    patt = re.compile(r'inet\s*\w*\S*:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    resp = [ip for ip in patt.findall(ifc_resp[0]) if ip != '127.0.0.1']
    if resp == []:
        log.warning("Couldn't determine IP Address, using 127.0.0.1.")
        return '127.0.0.1'
    return resp[0]

if __name__=='__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    SD = SlaveDriver(master_uri=sys.argv[1])
#    SD.run()



