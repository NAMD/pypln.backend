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
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfile)
        self.nodes = eval(self.config.get('cluster','nodes'))
        if bootstrap:
            self.__bootstrap_cluster()
    def __bootstrap_cluster(self):
        u"""
        Connect to the nodes and make sure they are ready to join the cluster
        :return:
        """
        #Start the Streamer
        self.streamer = Streamer(dict(self.config.items('streamer')))
        self.streamer.start()



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
        context = zmq.Context(1)
        # Socket facing Manager
        frontend = context.socket(zmq.PULL)
        frontend.bind("tcp://*:5559")

        # Socket facing slave nodes
        backend = context.socket(zmq.PUSH)
        backend.bind("tcp://*:5560")

        # Socket to reply to status requests
        monitor = context.socket(zmq.REP)
        monitor.bind("tcp://%:%"%(self.ipaddress,))

        zmq.device(zmq.STREAMER, frontend, backend)


        sub_slaved_sock = context.socket(zmq.SUB)
#        sub_slaved_sock.setsockopt(zmq.HWM, 1)

        log.info('Starting the Streamer on {0}'.format(self.ipaddress))
        sub_slaved_sock.bind(pub_uri)

        try:
            while True:
                package = frontend.recv_json()
                backend.send_json(package)
        except KeyboardInterrupt:
            frontend.close()
            backend.close()



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