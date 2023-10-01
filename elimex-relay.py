#!/usr/bin/env python3

"""This script could control https://elimex.bg/product/79420-modul-wi-fi-8-releta
"""

import socket
import json
from time import sleep
import argparse

PORT = 80  # The port used by the server

CMD_EP = 'POST /web_control.lua \r\n'
READ = 'Content-Length: 32\r\n\r\n{"id":"driveRel","action":"get"}'
TOGGLE = 'Content-Length: 30\r\n\r\n{"id":"driveRel","button":'

def send_command(host: str, command: str, verbose=False):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, PORT))
            buffer = bytes(CMD_EP + command, 'ascii')
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
        if verbose:
            print("Socket error %s." %(err))
        return (False, "")

def toggle_button(host, number):
    command = TOGGLE + "{}".format(number) + '}'
    send_command(host, command)

def switch_on_all_button(host, ):
    toggle_button(host, 9)

def switch_off_all_buttons(host, ):
    toggle_button(host, 10)

def read_button_state(host, number):
    if number < 1 or number > 8:
        return False, False

    ok, response = send_command(host, READ)
    if not ok:
        return False, False

    object =  json.loads(response)
    status = int(object['status'], 16)
    state = True if status & 1 << (number - 1) else False
    return True, state

def switch_on_button(host, number):

    if number < 1 or number > 8:
        return

    ok, on = read_button_state(host, number)
    if not ok or on:
        return

    toggle_button(host, number)

def switch_off_button(host, number):

    if number < 1 or number > 8:
        return

    ok, on = read_button_state(host, number)
    if not ok or not on:
        return

    toggle_button(host, number)

def test_api(host):

    switch_off_all_buttons(host)

    while True:

        send_command(host, READ)
        for num in range (1, 9):
            switch_on_button(host, num)

        switch_on_button(host, 4)

        send_command(host, READ)
        for num in range(1, 9):
            toggle_button(host, num)

        switch_off_button(host, 5)

        send_command(host, READ)
        for num in range(1, 9):
            toggle_button(host, num)

        send_command(host, READ)
        switch_off_all_buttons(host)

        send_command(host, READ)
        for num in range (1, 9):
            switch_off_button(host, num)

if __name__ == '__main__':

    args = argparse.ArgumentParser()
    args.add_argument('--ip', dest='address', type=str, required=True,
                      help='IP address of RelayPCB')
    args.add_argument('--on', dest='on', action='append', type=int,
                      choices=range(1, 9), help='Turn ON relay <number>')
    args.add_argument('--off', dest='off', action='append', type=int,
                      choices=range(1, 9), help='Turn OFF relay <number>')
    args = args.parse_args()

    if args.on:
        for num in args.on:
            switch_on_button(args.address, num)

    if args.off:
        for num in args.off:
            switch_off_button(args.address, num)



