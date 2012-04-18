#-*- coding:utf-8 -*-
"""
Graphite monitoring module.

This Module pushes information to graphite.
"""
__author__="flavio"
__date__ ="$21/07/2011 12:03:34$"


import sys
import time
import os
import platform 
import subprocess
from socket import socket
import zmq

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003

delay = 60 
if len(sys.argv) > 1:
    delay = int( sys.argv[1] )
  
context = zmq.Context()
# Subscribe to task batch finish message from sinks
batch_fin = context.socket(zmq.SUB)
batch_fin.connect("tcp://127.0.0.1:5560")
batch_fin.setsockopt(zmq.SUBSCRIBE,"sink-finished") #only hear to msgs starting with "sink-finished"
# Subscribe to vetilator pubs, to get information about remaining results
tasks = context.socket(zmq.SUB)
tasks.connect("tcp://127.0.0.1:%s"%5559)
tasks.setsockopt(zmq.SUBSCRIBE,"task-sent:") #only hear to msgs starting with "task-sent:"
# Initialize poll set
poller = zmq.Poller()
poller.register(batch_fin, zmq.POLLIN)
poller.register(tasks, zmq.POLLIN)

sock = socket()
try:
    sock.connect( (CARBON_SERVER,CARBON_PORT) )
except:
    print "Couldn't connect to Graphite, %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
    sys.exit(1)

while True:
    if platform.system() == "Linux":
        loadavg = open('/proc/loadavg').read().strip().split()[:3]
    now = int( time.time() )
    lines = []
    socks = dict(poller.poll())

    if tasks in socks and socks[tasks] == zmq.POLLIN:
        tasks = tasks.recv()
    # process tasks

    if batch_fin in socks and socks[batch_fin] == zmq.POLLIN:
        finished = batch_fin.recv()
    # process batch finishing
    
    lines.append("system.loadavg_1min %s %d" % (loadavg[0],now))
    lines.append("system.loadavg_5min %s %d" % (loadavg[1],now))
    lines.append("system.loadavg_15min %s %d" % (loadavg[2],now))
    lines.append("tasks.started %s %d"%(tasks, now))
    lines.append("tasks.finished %s %d"%(finished, now))
    message = '\n'.join(lines) + '\n' #all lines must end in a newline
    print "sending message\n"
    print '-' * 80
    print message
    print
    sock.sendall(message)
    time.sleep(delay)
