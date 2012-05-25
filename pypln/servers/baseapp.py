#-*- coding:utf-8 -*-
"""
Basic application setup classes
"""

__docformat__ = "restructuredtext en"

from multiprocessing import Process, ProcessError
import nmap


class TaskVentilator(object):
    """Class that sets up a task ventilator pattern"""
    def __init__(self, ventilator_class, worker_class, sink_class, nw,
                 ports={}):
        """
        Starts all the processes necessary for the ventilator pattern.

        :param ventilator_class: Class which will serve as ventilator.
        :param worker_class: Class which will serve as workers
        :param sink_class: Class which will serve as  sink
        :param nw: Number of workers
        :param ports: Dictionary with ports for all processes: {'ventilator':(pushport,pubport,subport),
        'worker':(pushport,pullport,subport),
        'sink':(pullport,pubport,subport)}
        :return: None
        """
        if not ports:
            self.ports = ports = self.find_ports()
        self.ventilator = ventilator_class(pushport=ports['ventilator'][0],
                                           pubport=ports['ventilator'][1],
                                           subport=ports['ventilator'][2])
        self.workers = [worker_class(pushport=ports['worker'][0],
                                     pullport=ports['worker'][1],
                                     subport=ports['worker'][2]) \
                        for i in xrange(nw)]
        self.sink = sink_class(pullport=ports['sink'][0],
                               pubport=ports['sink'][1],
                               subport=ports['sink'][2])

    @classmethod
    def find_ports(self, rng=(5500, 5600)):
        """
        Generate port set for this pattern by searching available ports
        This pattern require a total of 4 ports.
        :param rng: tuple with range of ports to search
        :return: Dictionary with ports for all processes: {'ventilator':(pushport,pubport,subport),
        'worker':(pushport,pullport,subport),
        'sink':(pullport,pubport,subport)}
        """
        nm = nmap.PortScanner()
        nm.scan('127.0.0.1', '{}-{}'.format(*rng))
        allp = nm['127.0.0.1'].all_protocols()
        openports = {} if 'tcp' not in allp else nm['127.0.0.1']['tcp']
        ports = {}
        available = []
        for p in range(*rng):
            if p not in openports:
                available.append(p)
            if len(available) == 4:
                break
        ports['ventilator'] = (available[0], available[1], available[2])
        ports['worker'] = (available[3], available[0], available[2])
        ports['sink'] = (available[3], available[2], available[1])
        return ports

    def spawn(self):
        """
        Start the subprocesses.
        :return: (ventilator, [w1, w2, ..., wn], sink)
                  All but ventilator are Process objects
        """
        workers = []
        for index, worker in enumerate(self.workers):
            process = Process(target=worker, name='worker-{}'.format(index))
            workers.append(process)
            process.start()
        sink = Process(target=self.sink, name='sink')
        sink.start()
        return self.ventilator, workers, sink
