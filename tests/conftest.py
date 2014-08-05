# -*- coding: utf-8 -*-

import pytest
from adhs.server import AdhsServer

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
