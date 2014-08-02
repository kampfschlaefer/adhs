# -*- coding: utf-8 -*-

import logging
import threading
import zmq


class AdhsServer(object):
    def __init__(self, data_socket='tcp://127.0.0.1:14005'):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.context = zmq.Context()
        self.replier = self.context.socket(zmq.REP)
        self.replier.set(zmq.RCVTIMEO, 25)
        self.replier.set(zmq.SNDTIMEO, 100)
        self.replier.bind(data_socket)

        self._data = {}

    def process(self):
        try:
            msg = self.replier.recv_multipart()
            self.logger.debug("Received msg %s", msg)
            if msg[0] == 'SAVE':
                self._data[msg[1]] = msg[2]
                self.replier.send_multipart(['OK'] + msg[1:])
            if msg[0] == 'GET':
                try:
                    val = self._data[msg[1]]
                    self.replier.send_multipart(['OK', msg[1], val])
                except KeyError:
                    self.replier.send_multipart(['KeyError'])
        except zmq.ZMQError:
            ''' timeout on receiving '''
            pass

    #def connectto(self, servers):
        #if not isinstance(servers, list):
        #    servers = [servers]
        #self.logger.error('Should announce myself to servers %s now', servers)

    #def connected_servers(self):
        #return []

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