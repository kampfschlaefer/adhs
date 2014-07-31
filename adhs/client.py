# -*- coding: utf-8 -*-

import logging


class AdhsClient(object):
    def __init__(self, servers=['tcp://localhost:14005']):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.error('Should connect to servers %s now', servers)

    def active_servers(self):
        '''Get the list of active servers'''
        return []