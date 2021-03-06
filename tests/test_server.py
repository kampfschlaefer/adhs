# -*- coding: utf-8 -*-

import pytest
import time

from adhs.server import AdhsServer

@pytest.yield_fixture
def oneserver():
    server = AdhsServer()
    yield server
    server.stop()


class TestOneServer(object):
    def test_start_one_server(self, oneserver):
        server = oneserver
        ## no key-values stored so far
        assert len(server.known_hashes()) == 0
        ## one known server: the server itself!
        assert len(server.known_servers()) == 1

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


class TestTwoServers(object):

    def loopservers(self, timeout, servers):
        start = time.time()
        while time.time() - start < timeout:
            for s in servers:
                s.process()

    def test_start_two_servers(self, twoservers):
        self.loopservers(2, twoservers)

        for s in twoservers:
            assert len(s.known_servers()) == 2

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

        self.loopservers(2, twoservers)

        assert server1.known_hashes() == hashes
        assert server2.known_hashes() == hashes

        assert server1._data == { hash(k): v for k,v in data }
        assert server2._data == { hash(k): v for k,v in data }
