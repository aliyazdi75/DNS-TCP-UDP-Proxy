import base64
import socket

import select
from tinydb import Query
from tinydb import TinyDB

import UDP_Transmit

HTTPCacheDB = TinyDB('HTTPCacheDB.json')
my_query = Query()

my_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# my_soc.settimeout(3)
my_soc.bind(('0.0.0.0', 8080))

while True:
    print('Waiting for client data...')
    request, address = UDP_Transmit.receive(my_soc)

    print('Received data from ', address[0])
    cached = HTTPCacheDB.search(my_query.request == request)

    if cached:
        print('Founded in cache.')
        UDP_Transmit.send(str(base64.b64decode(bytes(cached[0]['response'], encoding='ascii')), encoding='utf_8'),
                          my_soc, address)
        continue

    tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp = request[request.find('Host: ') + 6:]
    host = temp[:temp.find('\n')]

    try:
        tcp_soc.connect((host, 80))
    except Exception as e:
        print('Bad Request!', e.args)
        UDP_Transmit.send('\n\nBad Host!', my_soc, address)
        continue

    print('Sending request to main server...')
    tcp_soc.send(bytes(request, encoding='utf_8'))

    print('Request sent to', host)
    r = [tcp_soc]

    print('Waiting for response...')
    http_response = b''

    while r:
        r, w, e = select.select([tcp_soc], [], [], 5)
        if not r:
            break
        temp = tcp_soc.recv(1024)
        if not temp:
            break
        http_response += temp

    print('Response received!')
    http_response = http_response.replace(b'\r', b'')

    print('Sending response to client...')
    print(http_response)

    UDP_Transmit.send(str(http_response, encoding='ISO-8859-1'), my_soc, address)
    print('Saving to cache...')

    store = {
        'request': request,
        'response': str(base64.b64encode(http_response), encoding='ascii')
    }

    HTTPCacheDB.insert(store)
    print('Response sent!')
    tcp_soc.close()

# GET / HTTP/1.1
# Host: www.google.com