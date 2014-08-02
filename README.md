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
 - [ ] Autobalance of data with redundancy between servers
 - [ ] Auto-rebalance on server-failure
 - [ ] Load-Balancing from clients to servers
 - [x] Simple exists/set/get/delete operations for key-value pairs on the client