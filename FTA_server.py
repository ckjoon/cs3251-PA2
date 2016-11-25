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
          if debug:
            print('[DEBUG]file exists')
          conn.send_data('EXST'.encode('utf-8'))
          with open(os.path.join('serverf', fname), 'r+b') as f:
            data = f.read()
          if debug:
            print('[DEBUG]data read successfully: {}'.format(data))
          conn.send_data(data)
          if debug:
            print('[DEBUG]data sent successfully: {}'.format(data))
        else:
          if debug:
            print('[DEBUG]file does NOT exists')
          conn.send_data('NONE'.encode('utf-8'))

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

if __name__ == '__main__':
  args = get_args()
  global port, debug, window
  port = args.port
  debug = args.debug
  main()