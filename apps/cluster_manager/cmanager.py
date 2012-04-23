# -*- coding: utf-8 -*-
u"""
This executable is the manager of a pypln cluster. All tasks should be started through it and are
monitorable/controllable through it.

Cluster configuration must be specified on a config file pypln.conf
with at least the following sections:
[cluster]
nodes = x.x.x.x, x.x.x.x # list of IPs to add to PyPLN cluster

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
import multiprocessing

log = logging.getLogger(__name__)

class Manager(object):
    def __init__(self, configfile='/etc/pypln.conf'):
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfile)
    def __bootstrap_cluster(self):
        u"""
        Connect to the nodes and make sure they are ready to join the cluster
        :return:
        """
        pass



# Code below lifted of salt's master. for inspiration. still needs to be adapted.

class Publisher(multiprocessing.Process):
    '''
    The publishing interface, a simple zeromq publisher that sends out the
    commands.
    '''
    def __init__(self, opts):
        super(Publisher, self).__init__()
        self.opts = opts

    def run(self):
        '''
        Bind to the interface specified in the configuration file
        '''
        context = zmq.Context(1)
        pub_sock = context.socket(zmq.PUB)
        pub_sock.setsockopt(zmq.HWM, 1)
        pull_sock = context.socket(zmq.PULL)
        pub_uri = 'tcp://{0[interface]}:{0[publish_port]}'.format(self.opts)
        pull_uri = 'ipc://{0}'.format(
            os.path.join(self.opts['sock_dir'], 'publish_pull.ipc')
        )
        log.info('Starting the Salt Publisher on {0}'.format(pub_uri))
        pub_sock.bind(pub_uri)
        pull_sock.bind(pull_uri)

        try:
            while True:
                package = pull_sock.recv()
                pub_sock.send(package)
        except KeyboardInterrupt:
            pub_sock.close()
            pull_sock.close()


class ReqServer(object):
    '''
    Starts up the `Manager` request server, node Apps send status reports to this
    interface.
    '''
    def __init__(self, opts, crypticle, key, mkey):
        self.opts = opts
        self.master_key = mkey
        self.context = zmq.Context(self.opts['worker_threads'])
        # Prepare the zeromq sockets
        self.uri = 'tcp://%(interface)s:%(ret_port)s' % self.opts
        self.clients = self.context.socket(zmq.ROUTER)
        self.workers = self.context.socket(zmq.DEALER)
        self.w_uri = 'ipc://{0}'.format(
            os.path.join(self.opts['sock_dir'], 'workers.ipc')
        )
        # Prepare the AES key
        self.key = key
        self.crypticle = crypticle

    def __bind(self):
        '''
        Binds the reply server
        '''
        log.info('Setting up the master communication server')
        self.clients.bind(self.uri)
        self.work_procs = []

        for ind in range(int(self.opts['worker_threads'])):
            self.work_procs.append(MWorker(self.opts,
                self.master_key,
                self.key,
                self.crypticle,
                self.aes_funcs,
                self.clear_funcs))

        for ind, proc in enumerate(self.work_procs):
            log.info('Starting Salt worker process {0}'.format(ind))
            proc.start()

        self.workers.bind(self.w_uri)

        zmq.device(zmq.QUEUE, self.clients, self.workers)

    def start_publisher(self):
        '''
        Start the salt publisher interface
        '''
        # Start the publisher
        self.publisher = Publisher(self.opts)
        self.publisher.start()

    def run(self):
        '''
        Start up the ReqServer
        '''
        self.__bind()