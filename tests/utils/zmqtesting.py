# -*- coding: utf-8 -*-
u"""
This module contains various functions and classes to support testing.
Lifted from https://bitbucket.org/ssc/pyzmq-article/src/tip/example_app/test/support.py

license: GPL v3 or later
4/29/12
"""

__docformat__ = "restructuredtext en"

import time
import sys

from zmq.utils import jsonapi as json
import zmq


def make_sock(context, sock_type, bind=None, connect=None):
    """
    Creates a *sock_type* typed socket and binds or connects it to the given
    address.

    """
    sock = TestSocket(context, sock_type)
    if bind:
        sock.bind('tcp://%s:%s' % bind)
    elif connect:
        sock.connect('tcp://%s:%s' % connect)

    return sock


def get_forwarder(func):
    """Returns a simple wrapper for *func*."""
    def forwarder(*args, **kwargs):
        return func(*args, **kwargs)

    return forwarder


def get_wrapped_fwd(func):
    """
    Returns a wrapper, that tries to call *func* multiple time in non-blocking
    mode before rasing an :class:`zmq.ZMQError`.

    """
    def forwarder(*args, **kwargs):
        for i in xrange(100):
            try:
                rep = func(*args, flags=zmq.NOBLOCK, **kwargs)
                return rep

            except zmq.ZMQError:
                time.sleep(0.01)

        msg = 'Could not %s message.' % func.__name__[:4]
        raise zmq.ZMQError(msg)

    return forwarder


class TestSocket(object):
    """
    Wraps ZMQ :class:`~zmq.core.socket.Socket`. All *recv* and *send* methods
    will be called multiple times in non-blocking mode before a
    :class:`zmq.ZMQError` is raised.

    """
    def __init__(self, context, sock_type):
        self._context = context

        sock = context.socket(sock_type)
        self._sock = sock

        forwards = [  # These methods can simply be forwarded
                      sock.bind,
                      sock.bind_to_random_port,
                      sock.connect,
                      sock.close,
                      sock.setsockopt,
                      ]
        wrapped_fwd = [  # These methods are wrapped with a for loop
                         sock.recv,
                         sock.recv_json,
                         sock.recv_multipart,
                         sock.recv_unicode,
                         sock.send,
                         sock.send_json,
                         sock.send_multipart,
                         sock.send_unicode,
                         ]

        for func in forwards:
            setattr(self, func.__name__, get_forwarder(func))

        for func in wrapped_fwd:
            setattr(self, func.__name__, get_wrapped_fwd(func))


class ProcessTest(object):
    """
    Base class for process tests. It offers basic actions for sending and
    receiving messages and implements the *run* methods that handles the
    actual test generators.

    """
    def send(self, socket, header, body, extra_data=[]):
        """
        JSON-encodes *body*, concatenates it with *header*, appends
        *extra_data* and sends it as multipart message over *socket*.

        *header* and *extra_data* should be lists containg byte objects or
        objects implementing the buffer interface (like NumPy arrays).

        """
        socket.send_multipart(header + [json.dumps(body)] + extra_data)

    def recv(self, socket, json_load_index=-1):
        """
        Receives and returns a multipart message from *socket* and tries to
        JSON-decode the item at position *json_load_index* (defaults to ``-1``;
        the last element in the list). The original byte string will be
        replaced by the loaded object. Set *json_load_index* to ``None`` to get
        the original, unchanged message.

        """
        msg = socket.recv_multipart()
        if json_load_index is not None:
            msg[json_load_index] = json.loads(msg[json_load_index])
        return msg

    def run(self, testfunc):
        """
        Iterates over the *testfunc* generator and executes all actions it
        yields. Results will be sent back into the generator.

        :param testfunc: A generator function that yields tuples containing
                an action keyword, which should be a function of this or
                the inheriting class (like ``send`` or ``recv``) and additional
                parameters that will be passed to that function, e.g.:
                ``('send', socket_obj, ['header'], 'body')``
        :type testfunc:  generatorfunction

        """
        item_gen = testfunc()
        item = next(item_gen)

        def throw_err(skip_levels=0):
            """
            Throws the last error to *item_gen* and skips *skip_levels* in
            the traceback to point to the line that yielded the last event.

            """
            etype, evalue, tb = sys.exc_info()
            for i in range(skip_levels):
                tb = tb.tb_next
            item_gen.throw(etype, evalue, tb)

        try:
            while True:
                try:
                    ret = getattr(self, item[0])(*item[1:])
                    item = item_gen.send(ret)

                except zmq.ZMQError:
                    throw_err(3)  # PyZMQ could not send/recv
                except AssertionError:
                    throw_err(1)  # Error in the test
        except StopIteration:
            pass