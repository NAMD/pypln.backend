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
import fabric
import zmq
import logging
from zmq.devices import ProcessDevice
from zmq.devices.monitoredqueuedevice import ProcessMonitoredQueue
import multiprocessing
import socket, subprocess, re

log = logging.getLogger(__name__)

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

        if bootstrap:
            self.__bootstrap_cluster()

    def bind(self):
        try:
            context = zmq.Context(1)
            # Socket to reply to requests
            self.monitor = context.socket(zmq.REP)
            self.monitor.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['replyport']))
            self.pusher = context.socket(zmq.PUSH)
            self.pusher.connect("tcp://%s:%s"%(self.ipaddress,self.localconf['pushport']))
            self.sub_slaved_sock = context.socket(zmq.SUB)
            self.sub_slaved_sock.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['sd_subport']))
        except KeyboardInterrupt:
            log.info('Bringing down Manager')
        finally:
            self.monitor.close()
            self.sub_slaved_sock.close()

    def __bootstrap_cluster(self):
        u"""
        Connect to the nodes and make sure they are ready to join the cluster
        :return:
        """
        #Start the Streamer
        self.streamer = Streamer(dict(self.config.items('streamer')))
        self.streamer.start()
        self.deploy_slaves()

    def push_load(self,messages):
        """
        Push a number of messages to streamer
        """
        for i,m in enumerate(messages):
            print i
            self.pusher.send_json(m)

    def deploy_slaves(self):
        """
        Start slavedrivers on slavenodes
        """
        pass



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
            frontend.bind("tcp://*:5559")

            # Socket facing slave nodes
            backend = context.socket(zmq.PUSH)
            backend.bind("tcp://*:5560")

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
        raise NameError("Couldn't determine IP Address.")
    return resp[0]