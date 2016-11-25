#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
#from socket import *
import traceback
from crp_api import *


def get_args():
  parser = argparse.ArgumentParser(description='Run TCP sensor.')
  parser.add_argument('-s', '--server', type=str, required=True, help='ip address of the server')
  parser.add_argument('-p', '--port', type=int, required=True, help='port of the server')
  parser.add_argument('-d', '--debug', action='store_true', help='debugging output')

  return parser.parse_args()

def handle_post(conn, fname):
  try:
    if os.path.exists(os.path.join('clientf', fname)):
      with open(os.path.join('clientf', fname), 'r+b') as f:
        data = f.read()
      conn.send_data('POST'.encode('utf-8'))
      #print('command sent')
      conn.send_data(fname.encode('utf-8'))
      #print('filename sent')
      conn.send_data(data)
      if debug:
        print('[DEBUG]data sent: {0}'.format(data))
      #print('data sent')
    else:
      print('File you are trying to POST does not exist')
  except:
    print(traceback.print_exc())
    print('Error while trying to post the file, please make sure the file name you provided is correct and try again.\n')

def handle_get(conn, fname):
  try:
    conn.send_data('GET'.encode('utf-8'))
    if debug:
      print('[DEBUG]command sent: GET')
    #print('command sent')
    conn.send_data(fname.encode('utf-8'))
    if debug:
      print('[DEBUG]filename sent: {}'.format(fname))
    #print('filename sent')
    data = conn.recv()
    print(data)
    if data == b'EXST':
      print('[DEBUG]file found')
      data = conn.recv()
      if debug:
        print('[DEBUG]data received successfully: {}'.format(data))
      with open(os.path.join('clientf', fname), 'w+b') as f:
        f.write(data)
      if debug:
        print('[DEBUG]data written successfully.')
    else:
      print('File with this name was not found on server, try another one.')
    #print('data sent')

  except:
    print(traceback.print_exc())
    print('Error while trying to get a file, please make sure the file name you provided is correct and try again.\n')

def main():
  possible_commands = {'disconnect', 'window', 'get', 'post', 'help'}
  try:
    global window
    connected = False
    client = CRPSocket(port=8591, debug=debug)
    while True:
      command = input('Type a command to continue. For the list of available commands, type \'help\': ')
      if debug:
        print('[DEBUG]user entered \'{}\'.\n'.format(command))
        if command.lower().split()[0] in possible_commands:
          print('[DEBUG]the command entered is valid\n')

      if command.lower() == 'help':
        print('\nThe available commands are:\n\n*connect: connects to the FTA server.\n*get F: downloads file named F from the server.\n*post F: uploads file F to the server.\n*window W: the maximum window size the client can receive\n*disconnect: terminate the connection gracefully\n')
      elif command.lower() == 'connect':
        if not connected:
          try:
            connection = client.connect(server, port)
            connected = True
            print('Connection to server {0} on port {1} established successfully!'.format(server,port))
          except:
            print(traceback.print_exc())
            print('Client was not able to connect to server {0} on port {1}, make sure your server address is correct!'.format(server, port))
        else:
          print('Cannot call \'call\' command: client is already connected to the server.\n')
      elif command.lower().split()[0] == 'post':
        if len(command.split()) != 2:
          print('Incorrect number of arguments for command \'post\': it must have one argument \'F\'\n')
          continue
        if connected:

          filename = command.split()[1]
          handle_post(connection, filename)
        else:
          print('Cannot post file until the connection is established. Please use \'connect\' command to connect to server before using \'post\' again.\n')

      elif command.lower().split()[0] == 'get':
        if len(command.split()) != 2:
          print('Incorrect number of arguments for command \'get\': it must have one argument \'F\'\n')
          continue
        if connected:
          filename = command.split()[1]
          handle_get(connection, filename)
        else:
          print('Cannot get file until the connection is established. Please use \'connect\' command to connect to server before using \'get\' again.\n')

      elif command.lower().split()[0] == 'window':

        if len(command.split()) != 2:
          print('Incorrect number of arguments for command \'window\': it must have one argument \'W\'\n')
          continue
        try:
          new_window_size = int(command.lower().split()[1])
          if new_window_size < 1:
            raise Exception()
          client.recv_window = new_window_size
          print('Receiwing window is set to size {}'.format(new_window_size))
        except:
          print('Invalid window size used for \'window\' command!\n')
      elif command.lower() == 'disconnect':
        connected = False
        client.initiate_close()
        break

      else:
        print('\nThe command you have entered is not recognized as valid, please try again.\n')
  except:
    print(traceback.print_exc())

if __name__ == '__main__':
  args = get_args()
  global server, port, debug, window
  server = args.server
  port = args.port
  debug = args.debug
  window = 1024
  main()