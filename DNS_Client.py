import socket

from jsonpickle import json

while True:
    my_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_soc.settimeout(50)
    my_soc.connect(('127.0.0.1', 6985))

    req = input('Enter your request like "type target server":\n')
    if req == '':
        break

    req_type, req_target, req_server = req.split()
    query = {
        'type': req_type,
        'target': req_target,
        'server': req_server,
    }

    while True:

        try:
            my_soc.send(bytes(json.dumps(query), encoding='utf_8'))
            response = my_soc.recv(1024)
            break
        except Exception as e:
            print(e.args, 'receive time out!')

    print(response)
    my_soc.close()
