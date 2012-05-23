# -*- coding: utf-8 -*-
"""
Testing module for cmanager.py

license: GPL v3 or later
"""
__docformat__ = "restructuredtext en"

import unittest
import subprocess
import ConfigParser
import time
import os
import signal
import shlex
import zmq
import psutil
from utils import zmqtesting
from pypln.apps.cluster.cmanager import Manager, get_ipv4_address
from pypln.apps.cluster.slavedriver import SlaveDriver

slave_driver_cmd = './pypln/apps/cluster/slavedriver.py {}:{}'
cluster_manager_cmd = shlex.split('./pypln/apps/cluster/cmanager.py -c tests/pypln.test.conf --nosetup')
class TestManagerComm(unittest.TestCase):
    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('tests/pypln.test.conf')
        localip = get_ipv4_address().strip()
        replyport = int(self.config.get('manager', 'replyport'))
        statusport = int(self.config.get('manager', 'statusport'))
        confport = int(self.config.get('manager', 'conf_reply'))
        streamerpushport = int(self.config.get('streamer', 'pushport'))
        cmd_slave = shlex.split(slave_driver_cmd.format(localip, confport))
        self.managerproc = subprocess.Popen(cluster_manager_cmd)
        self.sdproc = subprocess.Popen(cmd_slave)
        self.context = zmq.Context()
        self.req_sock = zmqtesting.make_sock(context=self.context, sock_type=zmq.REQ, connect=(localip, replyport))
        self.status_sock = zmqtesting.make_sock(context=self.context, sock_type=zmq.REQ, connect=(localip, statusport))
#        self.status_sock = self.context.socket(zmq.SUB)
#        self.status_sock.connect('tcp://%s:%s'%(localip,statusport))
        self.pull_from_streamer_sock = zmqtesting.make_sock(context=self.context, sock_type=zmq.PULL, connect=(localip, streamerpushport))

    def tearDown(self):
        self.req_sock.close()
        self.status_sock.close()
        self.pull_from_streamer_sock.close()
        os.kill(self.managerproc.pid, signal.SIGKILL)
        os.kill(self.sdproc.pid, signal.SIGKILL)
        self.managerproc.terminate()
        self.sdproc.terminate()
        self.context.term()

    def test_manager_send_one_message(self):
        self.req_sock.send_json({'jobid': self.managerproc.pid})
        msg = self.req_sock.recv_json()
        self.assertEqual(msg['ans'], 'Job queued')

    def testing_sending_many_messages(self):
        msgs = [{'jobid': i, 'data': 'spam eggs ham'} for i in range(10)]
        self.req_sock.send_json(msgs)
        msg = self.req_sock.recv_json()
        self.assertEqual(msg['ans'], 'Job queued')
        self.req_sock.send_json(msgs) # send again
        msg = self.req_sock.recv_json()
        self.assertEqual(msg['ans'], 'Job queued')

    def test_job_control(self):
        msgs = [{'jobid': i, 'data': 'eggs ham spam'} for i in range(10)]
        self.req_sock.send_json(msgs)
        msg = self.req_sock.recv_json()
        self.assertEqual(msg['ans'], 'Job queued')
        self.status_sock.send("status")
        msg = self.status_sock.recv_json()
        self.assertTrue(msg.has_key('cluster'))
        self.assertTrue(msg.has_key('active jobs'))
        self.assertTrue(isinstance(msg['cluster'],dict))
        self.assertTrue(isinstance(msg['active jobs'],list))

    def test_streamer(self):
        self.req_sock.send_json({'jobid':self.managerproc.pid})
        self.req_sock.recv_json()
        msg = self.pull_from_streamer_sock.recv_json()
        self.assertTrue(msg.has_key('jobid'))

    def test_get_SD_status(self):
        self.status_sock.send("status")
        msg = self.status_sock.recv_json()
        self.assertTrue(isinstance(msg['cluster'], dict))
        self.assertTrue(len(msg['cluster']) > 0,msg="Cluster status dict is empty: {0}".format(msg))


class TestManagerInst(unittest.TestCase):
    def setUp(self):
        self.M = Manager('tests/pypln.test.conf',False)

    def tearDown(self):
        self.M.monitor.close()
        self.M.confport.close()
        self.M.pusher.close()
        self.M.statussock.close()
        self.M.sub_slavedriver_sock.close()
        self.M.streamerdevice.join(timeout=1)
        self.M.context.term()

    def test_load_config_file(self):
        self.assertTrue(self.M.config.has_section('cluster'))
        self.assertTrue(self.M.config.has_section('zeromq'))
        self.assertTrue(self.M.config.has_section('authentication'))
        self.assertTrue(self.M.config.has_section('streamer'))
        self.assertTrue(self.M.config.has_section('slavedriver'))
        self.assertTrue(self.M.config.has_section('worker'))
        self.assertTrue(self.M.config.has_section('sink'))

#    @unittest.skip('Failing with "address already in use"')
    def test_socket_binding(self):
        p = psutil.Process(self.M.pid)
        cons = p.get_connections()
        len_cons = len(cons)
        self.assertTrue(len_cons >= 5) # there are a couple of other sockets which get opened but are not related to pypln


class TestSlavedriverInst(unittest.TestCase):
    """
    tests related with Slavedriver class instantiation
    """
    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('tests/pypln.test.conf')
        statusport = int(self.config.get('manager','statusport'))
        self.managerproc = subprocess.Popen(cluster_manager_cmd)
        self.localip = get_ipv4_address().strip()
        self.context = zmq.Context()
        self.status_sock = zmqtesting.make_sock(context=self.context, sock_type=zmq.REQ, connect=(self.localip, statusport))

    def tearDown(self):
        self.status_sock.close()
        self.context.term()
        os.kill(self.managerproc.pid, signal.SIGTERM)
        self.managerproc.terminate()
        os.kill(self.managerproc.pid, signal.SIGKILL)

#    @unittest.skip('Failing with "address already in use"')
    def test_fetch_conf(self):
        SD = SlaveDriver(self.localip + ":" + self.config.get('manager', 'conf_reply'))
        self.assertTrue(isinstance(SD.localconf,dict))
        self.assertTrue(SD.localconf.has_key('master_ip'))

#    @unittest.skip('Failing with "address already in use"')
    def test_socket_binding(self):
        SD = SlaveDriver(self.localip + ":" + self.config.get('manager', 'conf_reply'))
        p = psutil.Process(SD.pid)
        cons = p.get_connections()
        self.assertTrue(len(cons) >= 5)

    @unittest.skip('Freezing')
    def test_handle_checkin(self):
        SD = SlaveDriver(self.localip + ":" + self.config.get('manager', 'conf_reply'))
        SD.listen(5)
        time.sleep(2)
        self.status_sock.send("status")
        msg = self.status_sock.recv_json()
        self.assertEqual(SD.pid, msg['cluster'][SD.ipaddress]['pid'])
        self.assertTrue(msg['cluster'][SD.ipaddress].has_key('last_reported'),
                        "Manager did not get status message")
