#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
This executable is the manager of a pypln cluster. All tasks should be started through it and are
monitorable/controllable through it.

Cluster configuration must be specified on a config file pypln.conf
with at least the following sections:
[cluster]
master_ip = 127.0.0.1
nodes = ['127.0.0.1', '10.250.46.208'] # list of IPs to add to PyPLN cluster
[cluster]

[authentication]
sshkey =

[zeromq]
# number of threads per context
iothreads = 1

[manager]
pushport = 5570
replyport = 5550
sd_subport = 5562
conf_reply = 5551
statusport = 5552


#Daemon configuration
[streamer]
# Streamer ports must be in the range 5570-9
pullport = 5570
pushport = 5571

subport = 5573

[slavedriver]
# Slavedrivers ports should be in the range 5560-9
confport = 5551
pullport = 5571
pushport = 5561
pubport = 5562
subport = 5563

[worker]



[sink]
pubport=


license: GPL v3 or later
__date__ = 4 / 23 / 12
"""
__docformat__ = "restructuredtext en"

import ConfigParser
from fabric.api import local, abort, execute
import zmq
from zmq.core.error import ZMQError
import argparse
from zmq.devices import ProcessDevice, ThreadDevice
from zmq.devices.monitoredqueuedevice import ProcessMonitoredQueue
import multiprocessing
import socket, subprocess, re
import sys, os, signal, atexit
import time
from logger import make_log

# Setting up the logger
log = make_log("Manager")


global streamerpid
streamerpid = None

class Manager(object):
    def __init__(self, configfile='/etc/pypln.conf',bootstrap=False):
        """
        Manager daemon which acts as cluster controller
        :param configfile: path to pypln.conf
        :param bootstrap: if a cluster should be bootstrapped upon instantiation
        """
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfile)
        self.nodes = eval(self.config.get('cluster','nodes'))
        self.node_registry = {}
        self.active_jobs = []
        self.localconf = dict(self.config.items('manager'))
        self.ipaddress = get_ipv4_address()
        self.localconf['master_ip'] = self.ipaddress
        self.stayalive = True
        self.streamerdevice = None
        self.bind()

        if bootstrap:
            self.__bootstrap_cluster()


    def run(self):
        """
        Infinite loop listening to request
        :return:
        """
        try:
            while self.stayalive:
#                self.statussock.send_json({'cluster':self.node_registry,'active jobs':self.active_jobs})
#                print "====> Publishing status"
                socks = dict(self.poller.poll())
                if self.monitor in socks and socks[self.monitor] == zmq.POLLIN:
                    jobmsg = self.monitor.recv_json()
                    self.process_jobs(jobmsg)
                    self.monitor.send_json({'ans':'Job queued'})
#                if self.monitor in socks and socks[self.monitor] == zmq.POLLOUT:
#                    pass
##                    self.monitor.send_json("{ans:'Job queued'}")

                if self.confport in socks and socks[self.confport] == zmq.POLLIN:
                    msg = self.confport.recv_json()
                    configmsg = self.handle_checkins(msg)
                    self.confport.send_json(configmsg)
#                if self.confport in socks and socks[self.confport] == zmq.POLLOUT:
#                    self.confport.send_json(configmsg)
                if self.statussock in socks and socks[self.statussock] == zmq.POLLIN:
                    print "====> Sending status"
                    msg = self.statussock.recv()
                    self.statussock.send_json({'cluster':self.node_registry,'active jobs':self.active_jobs})

                if self.sub_slaved_port in socks and socks[self.sub_slaved_port] == zmq.POLLIN:
                    msg = self.sub_slaved_port.recv_json()

        except (KeyboardInterrupt, SystemExit):
            log.info("Manager coming down")
        except ZMQError as z:
            log.error("Failed messaging: %"%z)
            print "Failed messaging: %"%z
        finally:
            print "======> Manager coming down"
            log.warning("Manager coming down")
            self.monitor.close()
            self.confport.close()
            self.pusher.close()
            self.sub_slaved_port.close()
            self.context.term()
            if self.streamerdevice:
                self.streamerdevice.join()
            sys.exit()

    def handle_checkins(self,msg):
        """
        Handle the checkin messages from slavedrivers adding their information to a registry of nodes
        :param msg: checkin message
        :return:
        """
        if msg['type'] == 'slavedriver':
            configmsg = dict(self.config.items('slavedriver'))
            configmsg['master_ip'] = self.ipaddress
            self.node_registry[msg['ip']] = msg
        return configmsg

    def bind(self):
        """
        Create and bind all sockets
        :return:
        """
        try:
            self.context = zmq.Context(1)
            # Socket to reply to job requests
            self.monitor = self.context.socket(zmq.REP)
            self.monitor.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['replyport']))
            # Socket to reply to configuration requests
            self.confport = self.context.socket(zmq.REP)
            self.confport.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['conf_reply']))
            # Socket to push jobs to streamer
            self.pusher = self.context.socket(zmq.PUSH)
            self.pusher.connect("tcp://%s:%s"%(self.ipaddress,self.localconf['pushport']))
            # Socket to subscribe to subscribe to  slavedrivers status messages
            self.sub_slaved_port = self.context.socket(zmq.SUB)
            self.sub_slaved_port.connect("tcp://%s:%s"%(self.ipaddress,self.localconf['sd_subport']))
            # Socket to send status reports
            self.statussock = self.context.socket(zmq.REP)
            self.statussock.bind("tcp://%s:%s"%(self.ipaddress,self.localconf['statusport']))
            # Initialize poll set to listen on multiple channels at once
            self.poller = zmq.Poller()
            self.poller.register(self.monitor, zmq.POLLIN|zmq.POLLOUT)
            self.poller.register(self.confport, zmq.POLLIN|zmq.POLLOUT)
            self.poller.register(self.statussock, zmq.POLLOUT|zmq.POLLIN)
            self.poller.register(self.sub_slaved_port, zmq.POLLIN)
        except ZMQError:
            sys.exit(1)


    def __bootstrap_cluster(self):
        u"""
        Connect to the nodes and make sure they are ready to join the cluster
        :return:
        """
        global streamerpid
        #Start the Streamer
        self.setup_streamer(dict(self.config.items('streamer')))

#        self.__deploy_slaves()

    def setup_streamer(self,opts):
        ipaddress = get_ipv4_address()
        #TODO: to have this as a ProcessDevice, One needs to figure out how to kill it when manager ends.
        self.streamerdevice  = ThreadDevice(zmq.STREAMER, zmq.PULL, zmq.PUSH)
#        self.streamerdevice  = ProcessDevice(zmq.STREAMER, zmq.PULL, zmq.PUSH)
        self.streamerdevice.bind_in("tcp://%s:%s"%(ipaddress,opts['pullport']))
        self.streamerdevice.bind_out("tcp://%s:%s"%(ipaddress,opts['pushport']))
        self.streamerdevice.setsockopt_in(zmq.IDENTITY, 'PULL')
        self.streamerdevice.setsockopt_out(zmq.IDENTITY, 'PUSH')
        self.streamerdevice.start()


    def process_jobs(self,msg):
        """
        Process jobs received
        :param msg: json string speciying the job
        """
        dispatch_time = time.asctime()
        if isinstance(msg,list):
            for m in msg:
#                print m
                m['dispatched_on'] = dispatch_time
                self.pusher.send_json(m)
                self.active_jobs.append(m)
        else:
            msg['dispatched_on'] = dispatch_time
            self.pusher.send_json(msg)
            self.active_jobs.append(msg)
        if self.streamerdevice:
            log.info("sent msg to streamer")



    def __deploy_slaves(self):
        """
        Start slavedrivers on slavenodes
        """
        execute(spawn_slave,hosts=self.nodes,masteruri=self.ipaddress+':'+self.localconf['conf_reply'])

def spawn_slave(masteruri):
    """
    Fabric task to spawn a slavedriver on remote node
    :param masteruri:
    :return:
    """
    sdproc = subprocess.Popen(['./slavedriver.py','tcp://%s'%(masteruri)])
    return sdproc.pid

#@atexit.register
#def cleanup():
#    if self.streamerdevice:
#        self.streamerdevice.join()
##        os.kill(streamerpid,signal.SIGKILL)

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

if  __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Starts PyPLN's cluster manager")
    parser.add_argument('--conf', '-c', help="Config file",required=True)
    args = parser.parse_args()
    M = Manager(configfile=args.conf,bootstrap=1)
    M.run()
