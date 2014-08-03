# -*- coding: utf-8 -*-

import pytest
import time

from adhs.server import AdhsServer

@pytest.yield_fixture
def oneserver():
    server = AdhsServer()
    yield server
    server.stop()

def generatedata(count):
    data = []
    hashes = set()
    for i in xrange(count):
        data.append( ('/testitem%5i' % i, 'TESTDATA %5i' % i) )
        hashes.add(hash('/testitem%5i' % i))
    return data, hashes

@pytest.fixture
def testdata_ten():
    return generatedata(10)

@pytest.fixture
def testdata_thousand():
    return generatedata(1000)

class TestOneServer(object):
    def test_start_one_server(self, oneserver):
        server = oneserver
        assert len(server.known_hashes()) == 0
        assert len(server.known_servers()) == 0

    def test_check_one_element(self, oneserver):
        server = oneserver
        assert server.known_hashes() == set()

        assert ['OK', '/bla', 'BLUB'] == server.process_save('/bla', 'BLUB')
        assert len(server.known_hashes()) == 1
        assert server.known_hashes() == set([hash('/bla')])

        assert server.process_get('/bla') == ['OK', '/bla', 'BLUB']

        assert server.process_delete('/bla') == ['OK']

        assert server.known_hashes() == set()

    def test_check_ten_elements(self, oneserver, testdata_ten):
        data, hashes = testdata_ten
        server = oneserver
        for key, value in data:
            server.process_save(key, value)

        assert server.known_hashes() == hashes

        for key, value in data:
            assert server.process_get(key) == ['OK', key, value]

        for key, value in data:
            assert server.process_delete(key) == ['OK']

        assert server.known_hashes() == set()

    def test_check_thousand_elements(self, oneserver, testdata_thousand):
        data, hashes = testdata_thousand
        server = oneserver
        for key, value in data:
            server.process_save(key, value)

        assert server.known_hashes() == hashes

        for key, value in data:
            assert server.process_get(key) == ['OK', key, value]

        for key, value in data:
            assert server.process_delete(key) == ['OK']

        assert server.known_hashes() == set()

@pytest.fixture
def serveraddresses():
    return [
        ('ipc://server%i.data_sock' % i, 'ipc://server%i.pub_sock' % i)
        for i in xrange(1, 11)
    ]

@pytest.yield_fixture
def twoservers(serveraddresses):
    addresses = serveraddresses[:2]
    servers = []
    for data_s, pub_s in addresses:
        s = AdhsServer(data_s, pub_s)
        s.subscribeto([ server[1] for server in addresses])
        servers.append(s)

    yield servers

    for s in servers:
        s.stop()

class TestTwoServers(object):

    def loopservers(self, timeout, servers):
        start = time.time()
        while time.time() - start < timeout:
            for s in servers:
                s.process()

    def test_start_two_servers(self, twoservers):
        self.loopservers(2, twoservers)

        for s in twoservers:
            assert len(s.known_servers()) == 1

    def test_two_servers_one_item(self, twoservers):
        server1, server2 = twoservers

        # Make them detect each other
        self.loopservers(2, twoservers)

        server1.process_save('/bla', 'BLUB')

        self.loopservers(1, twoservers)

        assert len(server1.known_hashes()) == 1
        assert len(server2.known_hashes()) == 1

        assert server1._data == server2._data

    def test_two_servers_thousand_items(self, twoservers, testdata_thousand):
        data, hashes = testdata_thousand
        server1, server2 = twoservers

        self.loopservers(2, twoservers)

        for key, value in data:
            server1.process_save(key, value)

        self.loopservers(5, twoservers)

        assert server1.known_hashes() == hashes
        assert server2.known_hashes() == hashes

        assert server1._data == dict(data)
        assert server2._data == dict(data)
