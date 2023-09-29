import socket
import json
from time import sleep

HOST = "192.168.5.10"  # The server's hostname or IP address
PORT = 80  # The port used by the server

READ = 'POST /web_control.lua \r\nContent-Length: 32\r\n\r\n{"id":"driveRel","action":"get"}'
TOGGLE = 'POST /web_control.lua \r\nContent-Length: 30\r\n\r\n{"id":"driveRel","button":'

def send_command(command: str, verbose=False):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            buffer = bytes(command, 'ascii')
            sock.sendall(buffer)
            data = sock.recv(8*1024)
            response = str(data, 'ascii')

            if verbose:
                print(command)
                print(response)

            if len(response) != len('{"web":[],"status":"0x01","names":[]}'):
               return (False, "")

            return (True, response)
    except OSError as err:
        print("Socket error %s." %(err))
        return (False, "")

def toggle_button(number):
    command = TOGGLE + "{}".format(number) + '}'
    send_command(command)

def switch_on_all_button():
    toggle_button(9)

def switch_off_all_buttons():
    toggle_button(10)

def read_button_state(number):
    if number < 1 or number > 8:
        return False

    ok, response = send_command(READ)
    if not ok:
        return

    object =  json.loads(response)
    status = int(object['status'], 16)
    state = True if status & 1 << (number - 1) else False
    return state

def switch_on_button(number):
    if read_button_state(number):
        return
    command = TOGGLE + "{}".format(number) + '}'
    send_command(command)

def switch_off_button(number):
    if not read_button_state(number):
        return
    command = TOGGLE + "{}".format(number) + '}'
    send_command(command)

def read_all_buttons_state():
    command = READ
    response = send_command(command)
    return response

if __name__ == '__main__':

    while True:

        read_all_buttons_state()
        for num in range (1, 9):
            switch_on_button(num)

        switch_on_button(4)

        read_all_buttons_state()
        for num in range(1, 9):
            toggle_button(num)

        switch_off_button(5)

        read_all_buttons_state()
        for num in range(1, 9):
            toggle_button(num)

        read_all_buttons_state()
        switch_off_all_buttons()
        sleep(2)

        read_all_buttons_state()
        for num in range (1, 9):
            switch_off_button(num)

        sleep(2)
pass



