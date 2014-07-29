# -*- coding: utf-8 -*-

from adhs.client import AdhsClient
from adhs.server import AdhsServer

class TestClient(object):
    def test_reach_zero_servers(self):
        '''As no server is started, asking the number of servers should be 0'''
        c = AdhsClient()
        assert len(c.active_servers()) == 0

    def test_start_one_server(self):
        AdhsServer()

        c = AdhsClient()
        assert len(c.active_servers()) == 1