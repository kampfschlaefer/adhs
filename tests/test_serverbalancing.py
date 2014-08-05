# -*- coding: utf-8 -*-

import time
import pytest

from adhs.server import AdhsServer

@pytest.yield_fixture
def fiveservers(serveraddresses):
    servers = []
    for data_s, pub_s in serveraddresses[:5]:
        s = AdhsServer(data_s, pub_s)
        s.subscribeto([server[1] for server in serveraddresses[:5]])
        servers.append(s)

    yield servers

    for s in servers:
        s.stop()


class TestFiveServers(object):

    def loopservers(self, timeout, servers):
        start = time.time()
        while time.time() - start < timeout:
            for s in servers:
                s.process()

    def test_segments_of_five(self, fiveservers):
        self.loopservers(3, fiveservers)

        segments = []
        for s in fiveservers:
            segments.append(s.mysegments())

        assert sorted(segments, key=lambda item: item[0]) == [[0,1,2],[1,2,3],[2,3,4],[3,4,0],[4,0,1]]

    def test_balance_ten_over_five(self, fiveservers, testdata_ten):
        '''expect each server to hold 3/5th of the data, that is five servers storing three segments each for triple redundancy'''

        ## startup
        self.loopservers(3, fiveservers)
        assert len(fiveservers[0]._known_servers) == 5

        ## store data
        data, hashes = testdata_ten
        for k, v in data:
            assert fiveservers[0].process_save(k, v) == ['OK', k, v]

        ## allow some time to balance
        self.loopservers(2, fiveservers)

        ## check if data is stored and distributed
        for s in fiveservers:
            assert len(s.known_hashes()) == 10
            assert s.known_hashes() == hashes
            assert len(s._data) == 6