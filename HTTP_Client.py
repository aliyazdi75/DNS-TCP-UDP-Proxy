import socket

import UDP_Transmit

inp = '1'
packet = ''
while inp:
    inp = input()
    packet += inp + '\n'

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.settimeout(3)

while True:
    print('Sending request to proxy...')
    UDP_Transmit.send(packet, soc, ('localhost', 8080))

    print('Message sent successfully!')
    packet = ''

    print('Receiving the response...')
    response, address = UDP_Transmit.receive(soc)
    print('Received completed!')

    if '301' in response or '302' in response:
        index = response.find('Location: ')
        location = response[index + 10:response.find('\n', index)]

        print('Redirected to ', location)
        new_host = location[7:location.find('/', 7)]
        new_url = location[location.find('/', 7):-1]
        packet = 'GET ' + new_url + ' HTTP/1.1\nHost: ' + new_host + '\n\n'
    else:
        break

with open('output.html', 'w') as f:
    rsp = response[response.find('\n\n') + 2:]
    f.write(rsp)

print('Response wrote to "output.html"')
soc.close()
