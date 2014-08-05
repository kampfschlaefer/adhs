[![Build Status](https://travis-ci.org/kampfschlaefer/adhs.svg?branch=master)](https://travis-ci.org/kampfschlaefer/adhs)

# Arnolds Decentralized Hyperresilent Storage

I started writing a little decentralized, self-healing key-value store. Just for the fun of it.

Watch it grow on https://github.com/kampfschlaefer/adhs

## Test it

- checkout from github
- create and activate a python virtualenv
- `pip install -r requirements.txt` to install the dependencies (might be that you need libz)
- `py.test` to run the tests

## TODO

Almost all is on the todo list:

 - [ ] Several servers should find each other and talk to each other.
 - [ ] Load-Balancing the communication from clients to servers
 - [ ] Auto-rebalance on server-failure
 - [x] Autobalance of data with redundancy between servers<br>
   Its currently with a redundancy of three
 - [x] Distribution of data to all servers
 - [x] Basic communication between servers
 - [x] Simple exists/set/get/delete operations for key-value pairs on the client