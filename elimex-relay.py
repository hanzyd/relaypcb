#!/usr/bin/env python3

"""This script could control https://elimex.bg/product/79420-modul-wi-fi-8-releta
"""

import socket
import json
from time import sleep
import argparse

INITIAL_IP = '192.168.4.1'
PORT = 80  # The port used by the server

READ = '"id":"driveRel","action":"get"'
TOGGLE = '"id":"driveRel","button":"{}"'
RESET = '"id":"RESET"'

CONFIG = '"autocon":"1","id":"setST",'
SETTINGS = '"ssid":"{}","pswd":"{}","ip":"{}","sbm":"255.255.255.0","gw":"{}"'

def send_command(host: str, command: str, verbose=False):

    control_ep = 'POST /web_control.lua \r\n'
    content_length = 'Content-Length: {}\r\n\r\n'.format(len(command))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, PORT))
            request = control_ep + content_length +  '{' + command + '}'
            buffer = bytes(request, 'ascii')
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


def initial_setup(ssid, password, address, getaway):
    settings = SETTINGS.format(ssid, password, address, getaway)
    send_command(INITIAL_IP, CONFIG + settings);
    sleep(2)
    send_command(INITIAL_IP, RESET)


def toggle_button(host, number):
    command = TOGGLE.format(number)
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

    for _ in range(1, 20):

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


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--ip', dest='address', type=str, required=True,
                      help='IP address of RelayPCB')
    args.add_argument('--on', dest='on', action='append', type=int,
                      choices=range(1, 9), help='Turn ON relay <number>')
    args.add_argument('--off', dest='off', action='append', type=int,
                      choices=range(1, 9), help='Turn OFF relay <number>')
    args.add_argument('--test', dest='test', action='store_true',
                      help='Run tests')
    args.add_argument('--setup', dest='setup', action='store_true',
                      help='Perform initial setup')
    args.add_argument('--ssid', dest='ssid', type=str,
                      help='Access Point SSID')
    args.add_argument('--password', dest='password', type=str,
                      help='Access Point password')
    args.add_argument('--getaway', dest='getaway', type=str,
                      help='Network getaway IP address')

    args = args.parse_args()

    if args.setup:
        if not args.ssid or not args.password or not args.getaway:
            print('--setup requires --ip, --getaway, --ssid and --password')
        else:
            initial_setup(args.ssid, args.password, args.address, args.getaway)

    if args.test:
        test_api(args.address)

    if args.on:
        for num in args.on:
            switch_on_button(args.address, num)

    if args.off:
        for num in args.off:
            switch_off_button(args.address, num)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass



