#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from socket import *

def get_args():
  parser = argparse.ArgumentParser(description='Run TCP sensor.')
  parser.add_argument('-s', '--server', type=str, required=True, help='ip address of the server')
  parser.add_argument('-p', '--port', type=int, required=True, help='port of the server')
  return parser.parse_args()


def main():
  connect = input('Type in \'connect\' to connect: ')
  if connect == 'connect':
    try:
      client_socket = socket(AF_INET, SOCK_STREAM)
      client_socket.connect((server, port))
      print('connected')
    except:
      print ('Client was not able to connect to server, make sure your server address is correct!')
      return
    while True:
      command = input('What would you like the client to do? ')
      command_values = command.split()
      
    
      possible_commands = ['disconnect', 'window', 'get', 'post', 'help']
      
      if(command_values[0] in possible_commands):
        if command_values[0] == 'disconnect':
          client_socket.close()
          return
        if command_values[0] == 'window':
          print ('window')
        if command_values[0] == 'get':
          print('get')
        if command_values[0] == 'post':
          print('at post')
          client_socket.send(('FileName:'+command_values[1]).encode('utf-8'))
          f = open(command_values[1],'rb')
          l = f.read(1024)
          while (l):
              client_socket.send(l)
              l = f.readline()
          f.close()
          client_socket.send('EndPost'.encode('utf-8'))
          print('post')
          
      
      else:
        print('please put in your command again')
      


if __name__ == '__main__':
  args = get_args()
  global server, port
  server = args.server
  port = args.port
  main()

#./sensor-udp -s 172.17.0.3 -p 8591 –u 'Room100SE' -c 'eye<3sockets!' -r 68.2
