import socket
import time

import dns.resolver
from jsonpickle import json
from tinydb import Query
from tinydb import TinyDB

DNSCacheDB = TinyDB('DNSCacheDB.json')
request = Query()

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('0.0.0.0', 6985))
soc.listen(1)

while True:
    print('Waiting for client data...')
    client_soc, address = soc.accept()
    byteData = client_soc.recv(1024)
    if byteData == b'':
        continue
    byteData = json.loads(str(byteData, encoding='utf_8'))

    cached = DNSCacheDB.search((request.target == byteData['target']) & (request.type == byteData['type']))
    if cached:
        print('Founded in cache.')
        cached = cached[0]
        if int(time.time()) - cached['time'] <= cached['ttl']:
            byteData['response'] = cached['result']
            client_soc.send(bytes(json.dumps(byteData), encoding='utf_8'))
            client_soc.close()
            continue
        else:
            print('ttl is over!')
            DNSCacheDB.remove((request.target == byteData['target']) & (request.type == byteData['type']))

    print('Requested from server')
    response = []
    try:
        while not response:
            myResolver = dns.resolver.Resolver()
            myResolver.nameservers = [byteData['server']]
            dnsAnswer = myResolver.query(byteData['target'], byteData['type'])
            print('DNS answer received')
            authorative = bin(dnsAnswer.response.flags)[7]
            ttl = dnsAnswer.ttl
            response = [str(x) for x in dnsAnswer]
    except Exception as e:
        print(e.args, 'Error!')
        client_soc.send(bytes(e.args[0], encoding='utf_8'))
        continue
    except dns.exception.Timeout as e:
        print(e.args, 'Timeout!')
        client_soc.send(bytes(e.args[0], encoding='utf_8'))
        continue
    store = {
        'type': byteData['type'],
        'target': byteData['target'],
        'ttl': dnsAnswer.ttl,
        'time': int(time.time()),
        'response': response,
        'authority': '0'
    }

    DNSCacheDB.insert(store)
    byteData['response'] = response
    byteData['authority'] = authorative
    client_soc.send(bytes(json.dumps(byteData), encoding='utf_8'))
    client_soc.close()
