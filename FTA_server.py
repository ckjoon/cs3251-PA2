#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, threading, time, os.path, traceback
#from socket import *
from crp_api import *


def get_args():
  parser = argparse.ArgumentParser(description='Run ATCP Server.')
  parser.add_argument('-p', '--port', type=int, required=True, help='port of the server')
  parser.add_argument('-d', '--debug', action='store_true', help='debugging output')

  return parser.parse_args()

def listen(conn):
  cmd = None
  try:
    while True:
      cmd = conn.recv().decode('utf-8')
      if debug:
        print('[DEBUG]command received: {}'.format(cmd))
      if cmd == 'POST':
        fname = conn.recv().decode('utf-8')
        if debug:
          print('[DEBUG]filename received: {}'.format(fname))
        data = conn.recv()
        if debug:
          print('[DEBUG]data received successfully: {}'.format(data))
        with open(os.path.join('serverf', fname), 'w+b') as f:
          f.write(data)
        if debug:
          print('[DEBUG]data written successfully.')
        print('\nListening for new commands!')
      elif cmd == 'GET':
        fname = conn.recv().decode('utf-8')
        if debug:
          print('[DEBUG]filename received: {}'.format(fname))
        if os.path.exists(os.path.join('serverf', fname)):
          with open(os.path.join('serverf', fname), 'r+b') as f:
            data = f.read()
          if debug:
            print('[DEBUG]data read successfully: {}'.format(data))
          conn.send_data(data)
          if debug:
            print('[DEBUG]data sent successfully: {}'.format(data))
        print('\nListening for new commands!')

  except:
    print(traceback.print_exc())
    print('Error while listening.\n')

def main():
  try:
    global window
    #ip_addr = '172.17.0.3'
    server_port = port
    server = CRPSocket(port=server_port, server=True, debug=debug)
    print('Server is running on port {}!'.format(server_port))
    connection = server.accept()
    listen(connection)
    possible_commands = {'terminate', 'window', 'help'}
  except:
    print(traceback.print_exc())
'''
    while True:
      command = input('Type a command to continue. For the list of available commands, type \'help\': ')
      if debug:
        print('[DEBUG]user entered \'{}\'.\n'.format(command))
        if command.lower().split()[0] in possible_commands:
          print('[DEBUG]the command entered is valid')

      if command.lower() == 'help':
        print('The available commands are:\n\n*window W: the maximum window size the server can receive\n*terminate: shutdown the server gracefully\n')

      elif command.lower().split()[0] == 'window':
        try:
          new_window_size = int(command.lower().split()[1])
          if new_window_size < 1:
            raise Exception()
          client.recv_window = new_window_size
          print('Receiwing window is set to size {}'.format(new_window_size))
        except:
          print('Invalid window size used for \'window\' command!\n')

      elif command.lower() == 'terminate':
        client.initiate_close()
        break

      else:
        print('Command you entered is not recognized as valid, please try again.\n')
'''

if __name__ == '__main__':
  args = get_args()
  global port, debug, window
  port = args.port
  debug = args.debug
  main()