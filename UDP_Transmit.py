
def checksum(input_str):
    message = bytes(input_str,encoding='utf_8')
    checksum = sum(message)
    return str(checksum).zfill(5)


def send(input_message, socket, address):

    old_timeout = socket.gettimeout()
    socket.settimeout(3)
    response_parts = [input_message[i:i + 100] for i in range(0, len(input_message), 100)]
    messages = [checksum(x) + str(i % 2) + x for i, x in enumerate(response_parts)]

    end_message = '###end###'
    messages.append(checksum(end_message) + str(len(messages) % 2) + end_message)

    ack_flag = 0

    for message in messages:
        while True:
            try:
                socket.sendto(bytes(message, encoding='utf_8'), address)
                # print(message)
            except Exception as e:
                print(e.args)
                continue
            try:
                ack, client_address = socket.recvfrom(1024)
            except Exception as e:
                print(e.args)
                continue
            if int(str(ack, encoding='utf_8')) == ack_flag:
                ack_flag = (ack_flag + 1) % 2
                break
    socket.settimeout(old_timeout)


def receive(socket):

    message = ''
    while True:
        try:
            data, address = socket.recvfrom(1024)
            data = str(data, encoding='utf_8')
            if checksum(data[6:]) == data[:5]:
                socket.sendto(bytes(data[5], encoding='utf_8'), address)
                if data[6:] == '###end###':
                    break
                message += data[6:]
            else:
                print('Wrong checksum, expected', checksum(data[6:]), 'found', data[:5])
        except Exception as e:
            print(e.args)
    return message, address
