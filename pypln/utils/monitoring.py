#!/usr/bin/env python
# coding: utf-8

import socket
from time import time
import psutil


def get_outgoing_ip((host, port)):
    """Connect to remote host/port, return local IP used by OS"""
    #TODO: handle exception if can't connect and add a timeout
    raw_socket = socket.socket(socket.AF_INET)
    raw_socket.connect((host, port))
    data = raw_socket.getsockname()
    raw_socket.close()
    return data[0]

def get_host_info():
    """Return a ``dict`` with system's information

    `Example of its output <https://gist.github.com/gists/2891134>`_
    """
    memory_usage = psutil.phymem_usage()
    cached_memory = psutil.cached_phymem()
    buffered_memory = psutil.phymem_buffers()
    real_used = memory_usage.used - buffered_memory - cached_memory
    real_free = memory_usage.total - real_used
    percent = 100 * (float(memory_usage.used) / memory_usage.total)
    real_percent = 100 * (float(real_used) / memory_usage.total)
    virtual_used = psutil.used_virtmem()
    virtual_free = psutil.avail_virtmem()
    virtual_total = virtual_used + virtual_free
    info_per_nic = psutil.network_io_counters(pernic=True)
    network_info = {}
    for key, value in info_per_nic.iteritems():
        network_info[key] = {'bytes sent': value.bytes_sent,
                             'bytes received': value.bytes_recv,
                             'packets sent': value.packets_sent,
                             'packets received': value.packets_recv,}
    partitions = psutil.disk_partitions()
    storage_info = {}
    for partition in partitions:
        disk_usage = psutil.disk_usage(partition.mountpoint)
        storage_info[partition.device] = {'mount point': partition.mountpoint,
                                          'file system': partition.fstype,
                                          'total bytes': disk_usage.total,
                                          'total used bytes': disk_usage.used,
                                          'total free bytes': disk_usage.free,
                                          'percent used': disk_usage.percent,}
    return {'memory': {'free': memory_usage.free,
                       'total': memory_usage.total,
                       'used': memory_usage.used,
                       'cached': cached_memory,
                       'buffers': buffered_memory,
                       'real used': real_used,
                       'real free': real_free,
                       'percent': percent,
                       'real percent': real_percent,
                       'total virtual': virtual_total,
                       'used virtual': virtual_used,
                       'free virtual': virtual_free,},
            'cpu': {'number of cpus': psutil.NUM_CPUS,
                    'cpu percent': psutil.cpu_percent(),},
            'network': {'interfaces': network_info,},
            'storage': storage_info,
            'uptime': time() - psutil.BOOT_TIME,}

def get_process_info(process_id):
    """Return CPU and memory information for a given PID"""
    try:
        process = psutil.Process(process_id)
    except psutil.error.NoSuchProcess:
        return None
    memory_info = process.get_memory_info()
    return {'cpu percent': process.get_cpu_percent(),
            'resident memory': memory_info.rss,
            'virtual memory': memory_info.vms,
            'pid': process.pid,
            'started at': process.create_time,}


if __name__ == '__main__':
    from pprint import pprint
    from time import time
    from os import getpid

    host_info = get_host_info()
    host_info['network']['cluster ip'] = get_outgoing_ip(('localhost', 80))
    broker_info = get_process_info(getpid())
    broker_info['type'] = 'broker'
    broker_info['active workers'] = 4
    processes = [broker_info]
    for job in range(broker_info['active workers']):
        worker_info = get_process_info(getpid())
        if worker_info is not None:
            worker_info['worker'] = 'the worker is a lie'
            worker_info['data'] = '...'
            worker_info['type'] = 'worker'
            processes.append(worker_info)
    data = {'host': host_info, 'processes': processes, 'timestamp': time()}
    pprint(data)
