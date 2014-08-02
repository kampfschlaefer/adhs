# -*- coding: utf-8 -*-

import logging
import zmq


class AdhsClient(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self._active_servers = []

        self.context = zmq.Context()
        self.requester = self.context.socket(zmq.REQ)
        self.requester.set(zmq.RCVTIMEO, 100)
        self.requester.set(zmq.SNDTIMEO, 100)
        self.requester.set(zmq.IMMEDIATE, 1)

    def connectToServer(self, server='tcp://localhost:14005'):
        self.logger.info('connecting to %s', server)
        self.requester.connect(server)
        self._active_servers.append(server)

    def active_servers(self):
        '''Get the list of active servers'''
        return self._active_servers

    def get(self, key):
        if len(self._active_servers) == 0:
            raise KeyError
        self.requester.send_multipart(['GET', key])
        msg = self.requester.recv_multipart()
        print "received answer %s" % msg
        if msg[0] != 'OK':
            raise KeyError
        return msg[2]

    def save(self, key, value):
        if len(self._active_servers) == 0:
            raise ValueError
        self.requester.send_multipart(['SAVE', key, value])
        status, key, value = self.requester.recv_multipart()
        self.logger.info(
            'Status %s for saving key %s with value \'%s\'',
            status, key, value
        )