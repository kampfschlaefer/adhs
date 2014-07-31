# -*- coding: utf-8 -*-

import logging


class AdhsServer(object):
    def __init__(self, control_socket='tcp://*:14005'):
        self.logger = logging.getLogger(self.__class__.__name__)
        pass

    def connectto(self, servers):
        if not isinstance(servers, list):
            servers = [servers]
        self.logger.error('Should announce myself to servers %s now', servers)

    def connected_servers(self):
        return []

    def known_hashes(self):
        return []