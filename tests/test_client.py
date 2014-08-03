# -*- coding: utf-8 -*-

import pytest
import time

from adhs.client import AdhsClient
from adhs.server import AdhsServer, ServerThread

class TestServer(object):
    def test_start_one_server(self):
        server = AdhsServer() #'ipc://tmp.sock')
        assert len(server.known_hashes()) == 0
        assert len(server.known_servers()) == 0

    #@pytest.mark.xfail
    def test_start_two_servers(self):
        server_addresses = [
            ('ipc://server1.data_sock', 'ipc://server1.pub_sock'),
            ('ipc://server1.data_sock', 'ipc://server2.pub_sock')
        ]
        servers = []
        for data_s, pub_s in server_addresses:
            s = AdhsServer(data_s, pub_s)
            s.subscribeto([ server[1] for server in server_addresses])
            servers.append(s)

        start = time.time()
        while time.time() - start < 5:
            for s in servers:
                s.process()
            #print '.'
            #time.sleep(0.1)

        for s in servers:
            assert len(s.known_servers()) == 1


@pytest.yield_fixture
def adhsserver():
    t = ServerThread(data_socket='ipc://testserver.sock', pub_socket='ipc://testserver.pub_socket')
    t.start()
    while not t.is_alive():
        time.sleep(0.01)
    while t.server == None:
        time.sleep(0.01)
    time.sleep(0.2)
    yield t.server
    t.stop()
    t.join()


class TestClient(object):
    def test_reach_zero_servers(self):
        '''As no server is started, asking the number of servers should be 0'''
        c = AdhsClient()
        assert len(c.active_servers()) == 0

    def test_start_one_server(self, adhsserver):
        c = AdhsClient()
        c.connectToServer('ipc://testserver.sock')
        assert len(c.active_servers()) == 1
        assert len(adhsserver.known_hashes()) == 0

    def test_get_not_existing_value(self, adhsserver):
        c = AdhsClient()
        c.connectToServer('ipc://testserver.sock')
        with pytest.raises(KeyError):
            c.get('/bla')

    def test_search_non_existing_key(self, adhsserver):
        c = AdhsClient()
        c.connectToServer('ipc://testserver.sock')
        assert c.has_key('/bla') == False

    def test_search_existing_key(self, adhsserver):
        c = AdhsClient()
        c.connectToServer('ipc://testserver.sock')
        c.save('/bla', 'BLUB')
        assert c.has_key('/bla') == True
        assert c.has_key('/blub') == False

    #@pytest.mark.xfail
    def test_save_one_value(self, adhsserver):
        c = AdhsClient()
        c.connectToServer('ipc://testserver.sock')
        c.save('/bla', 'BLUB BLOB')
        assert len(adhsserver.known_hashes()) == 1

    #@pytest.mark.xfail
    def test_save_and_get_one_value(self, adhsserver):
        c = AdhsClient()
        c.connectToServer('ipc://testserver.sock')
        c.save('/bla', 'BLUB BLOB')
        assert c.get('/bla') == 'BLUB BLOB'

    def test_save_and_delete_one_value(self, adhsserver):
        c = AdhsClient()
        c.connectToServer('ipc://testserver.sock')
        c.save('/bla', 'BLUB')
        assert c.get('/bla') == 'BLUB'
        c.delete('/bla')
        assert c.has_key('/bla') == False
