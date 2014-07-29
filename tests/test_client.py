# -*- coding: utf-8 -*-

from adhs.client import AdhsClient

class TestClient(object):
    def test_reach_zero_servers(self):
        '''As no server is started, asking the number of servers should be 0'''
        c = AdhsClient()
        assert len(c.active_servers()) == 0