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
        try:
            msg = self.replier.recv_multipart()
            self.logger.debug("Received msg %s", msg)
            if msg[0] in self._actions:
                ret = self._actions[msg[0]](*msg[1:])
                self.replier.send_multipart(ret)
            else:
                self.replier.send_multipart(['INVALID COMMAND'])
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
