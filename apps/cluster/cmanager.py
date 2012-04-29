#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
This executable is the manager of a pypln cluster. All tasks should be started through it and are
monitorable/controllable through it.

Cluster configuration must be specified on a config file pypln.conf
with at least the following sections:
[cluster]
nodes = [x.x.x.x, x.x.x.x] # list of IPs to add to PyPLN cluster

[authentication]

[zeromq]
io_threads = 2



license: GPL v3 or later
__date__ = 4 / 23 / 12
"""
__docformat__ = "restructuredtext en"

#TODO: Complete usage docs to modules docstring

import ConfigParser
from fabric.api import local, abort, execute
import zmq
import logging
import logging.handlers
import argparse
from zmq.devices import ProcessDevice
from zmq.devices.monitoredqueuedevice import ProcessMonitoredQueue
import multiprocessing
import socket, subprocess, re

log = logging.getLogger(__name__)
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler('/tmp/pypln.log', maxBytes=20000, backupCount=1)
log.addHandler(handler)

class Manager(object):
    def __init__(self, configfile='/etc/pypln.conf',bootstrap=False):
        """

        :param configfile: path to pypln.conf
        :param bootstrap: if a cluster should be bootstrapped upon instantiation
        :return:
        """
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfile)
        self.nodes = eval(self.config.get('cluster','nodes'))
        self.localconf = dict(self.config.items('manager'))
        self.ipaddress = get_ipv4_address()
        self.stayalive = True
        self.bind()

        if bootstrap:
            self.__bootstrap_cluster()


    def run(self):
        """
        Infinite loop listening to request
        :return:
        """
        while self.stayalive:
            socks = dict(self.poller.poll())
            if self.monitor in socks and socks[self.monitor] == zmq.POLLIN:
                jobmsg = self.monitor.recv_json()
                self.process_jobs(jobmsg)
            if self.monitor in socks and socks[self.monitor] == zmq.POLLOUT:
                self.monitor.send_json("{ans:'Job queued'}")
            if self.confport in socks and socks[self.confport] == zmq.POLLIN:
                msg = self.confport.recv()
                if msg == 'slavedriver':
                    replymsg = dict(self.config.items('slavedriver'))

            if self.confport in socks and socks[self.confport] == zmq.POLLOUT:
                self.confport.send_json(replymsg)

            if self.sub_slaved_port in socks and socks[self.sub_slaved_port] == zmq.POLLIN:
                msg = self.sub_slaved_port.recv_json()
                print msg

    def bind(self):
        """
        Create and bind all sockets
        :return:
        """
        try:
            context = zmq.Context(1)
            # Socket to reply to job requests
            self.monitor = context.socket(zmq.REP)
            self.monitor.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['replyport']))
            # Socket to reply to configuration requests
            self.confport = context.socket(zmq.REP)
            self.confport.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['conf_reply']))
            # Socket to push jobs to streamer
            self.pusher = context.socket(zmq.PUSH)
            self.pusher.connect("tcp://%s:%s"%(self.ipaddress,self.localconf['pushport']))
            # Socket to subscribe to subscribe to  slavedrivers status messages
            self.sub_slaved_port = context.socket(zmq.SUB)
            self.sub_slaved_port.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['sd_subport']))
            # Initialize poll set to listen on multiple channels at once
            self.poller = zmq.Poller()
            self.poller.register(self.monitor, zmq.POLLIN)
            self.poller.register(self.confport, zmq.POLLIN|zmq.POLLOUT)
            self.poller.register(self.sub_slaved_port, zmq.POLLIN)
        except KeyboardInterrupt:
            log.info('Bringing down Manager')
#        finally:
#            self.monitor.close()
#            self.sub_slaved_port.close()

    def __bootstrap_cluster(self):
        u"""
        Connect to the nodes and make sure they are ready to join the cluster
        :return:
        """
        #Start the Streamer
        self.streamer = Streamer(dict(self.config.items('streamer')))
        self.streamer.start()
        self.__deploy_slaves()

    def process_jobs(self,msg):
        """
        :param msg: json string speciying the job
        """
        pass

    def __push_load(self,messages):
        """
        Push a number of messages to streamer
        """
        for i,m in enumerate(messages):
            print i
            self.pusher.send_json(m)

    def __deploy_slaves(self):
        """
        Start slavedrivers on slavenodes
        """
        pass
#        execute("./slavedriver",hosts= self.nodes)



class Streamer(multiprocessing.Process):
    '''
    The cluster control interface, containing a Streamer device, and a subscribe channel
    to listem to SlaveDrivers, on slave nodes.
    '''
    def __init__(self, opts):
        super(Streamer, self).__init__()
        self.opts = opts
        self.ipaddress = get_ipv4_address()


    def run(self):
        """
        Bind to the interface specified in the configuration file
        """
        try:
            context = zmq.Context(1)
            # Socket facing Manager
            frontend = context.socket(zmq.PULL)
            frontend.bind("tcp://%s:%s"%(self.ipaddress,self.opts['pullport']))

            # Socket facing slave nodes
            backend = context.socket(zmq.PUSH)
            backend.bind("tcp://%s:%s"%(self.ipaddress,self.opts['pushport']))

            zmq.device(zmq.STREAMER, frontend, backend)

            log.info('Starting the Streamer on {0}'.format(self.ipaddress))

        except KeyboardInterrupt:
            frontend.close()
            backend.close()
            context.term()



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
        log.warning("Couldn't determine IP Address.")
        return '127.0.0.1'
    return resp[0]

if  __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Starts PyPLN's cluster manager")
    parser.add_argument('--conf', '-c', help="Config file",required=True)
    args = parser.parse_args()
    M = Manager(configfile=args.conf,bootstrap=0)
    M.run()