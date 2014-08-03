# -*- coding: utf-8 -*-

import logging
import threading
import time
import zmq


class AdhsServer(object):
    def __init__(self, data_socket='tcp://127.0.0.1:14005', pub_socket='tcp://127.0.0.1:14010'):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.context = zmq.Context()
        self.replier = self.context.socket(zmq.REP)
        self.replier.bind(data_socket)
        self._data_socket = data_socket

        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(pub_socket)
        self._pub_socket = pub_socket
        self._last_heartbeat = 0

        self.poller = zmq.Poller()
        self.poller.register(self.replier, zmq.POLLIN)

        self._data = {}
        self._known_servers = {} # map of address: {'last_seen': time,}

        self._actions = {
            'EXISTS': self.process_exists,
            'GET': self.process_get,
            'SAVE': self.process_save,
            'DELETE': self.process_delete,
        }

    def process_exists(self, key):
        if key in self._data:
            return ['OK']
        return ['KeyError']

    def process_get(self, key):
        if key in self._data:
            return ['OK', key, self._data[key]]
        return ['KeyError']

    def process_save(self, key, value):
        self._data[key] = value
        return ['OK', key, value]

    def process_delete(self, key):
        if key in self._data:
            del self._data[key]
            return ['OK']
        return ['KeyError']

    def process(self):
        now = time.time()
        if now - self._last_heartbeat > 1:
            #print '%s will send heartbeat' % self._pub_socket
            self.publisher.send_multipart(['PING', self._pub_socket])
            self._last_heartbeat = now

        events = self.poller.poll(timeout=1)
        for socket, event in events:
            #print 'Received something on socket %s' % socket.fd
            if socket == self.replier:
                msg = self.replier.recv_multipart()
                self.logger.debug("Received msg %s", msg)
                if msg[0] in self._actions:
                    ret = self._actions[msg[0]](*msg[1:])
                    self.replier.send_multipart(ret)
                else:
                    self.replier.send_multipart(['INVALID COMMAND'])
            else: # Has to be one of the subscribers
                msg = socket.recv_multipart()
                if msg[0] == 'PING':
                    #print "Received a heartbeat from %s" % msg
                    if msg[1] not in self._known_servers:
                        self._known_servers[msg[1]] = {}
                    self._known_servers[msg[1]]['last_seen'] = time.time()

    def subscribeto(self, servers):
        if not isinstance(servers, list):
            servers = [servers]
        for server in servers:
            if server != self._pub_socket:
                #print 'subscribing to %s' % server
                socket = self.context.socket(zmq.SUB)
                socket.set(zmq.SUBSCRIBE, 'PING')
                socket.connect(server)
                self.poller.register(socket, zmq.POLLIN)

    def known_servers(self):
        return self._known_servers

    def known_hashes(self):
        return self._data.keys()


class ServerThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ServerThread, self).__init__()
        self._stop = False
        self.server = None
        self._args = (args, kwargs)

    def stop(self):
        self._stop = True

    def run(self):
        logger = logging.getLogger('ServerThread')
        logger.info('starting thread')
        self.server = AdhsServer(*self._args[0], **self._args[1])

        while not self._stop:
            self.server.process()

        logger.info('Stopped thread')
