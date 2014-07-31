# -*- coding: utf-8 -*-

from adhs.client import AdhsClient
from adhs.server import AdhsServer

class TestServer(object):
    def test_start_one_server(self):
        server = AdhsServer()
        assert len(server.connected_servers()) == 0

    def test_start_three_servers(self):
        server_addresses = ['icp://server1.sock', 'icp://server2.sock', 'icp://server3.sock']
        servers = []
        for s_addr in server_addresses:
            s = AdhsServer(s_addr)
            s.connectto(filter(lambda s: s == s_addr, server_addresses))
            servers.append(s)

        for s in servers:
            assert len(s.connected_servers()) == 2

    def test_known_hashes(self):
        server = AdhsServer()
        assert server.known_hashes() == []


class TestClient(object):
    def test_reach_zero_servers(self):
        '''As no server is started, asking the number of servers should be 0'''
        c = AdhsClient()
        assert len(c.active_servers()) == 0

    def test_start_one_server(self):
        AdhsServer()

        c = AdhsClient()
        assert len(c.active_servers()) == 1