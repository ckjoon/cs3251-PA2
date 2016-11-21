#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
from socket import *

def get_args():
  parser = argparse.ArgumentParser(description='Run TCP sensor.')
  parser.add_argument('-s', '--server', type=str, required=True, help='ip address of the server')
  parser.add_argument('-p', '--port', type=int, required=True, help='port of the server')
  parser.add_argument('-d', '--debug', action='store_true', help='debugging output')

  return parser.parse_args()

def main():
  try:
    connect = input('Type in \'connect\' to connect: ')
    while (connect != 'connect'):
      print('Incorrect input format')
      connect = input('Type in \'connect\' to connect: ')
    if connect == 'connect':
      try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server, port))
        if debug:
          print('The client is connected to server {0} on port {1}'.format(server,port))
      except:
        print ('Client was not able to connect to server, make sure your server address is correct!')
        return
      while True:
        command = input('What would you like the client to do? ')
        if debug:
          print('[DEBUG]user input: '+command)
        command_values = command.split()
        possible_commands = ['disconnect', 'window', 'get', 'post', 'help']
        if(command_values[0] in possible_commands):
          if debug:
              print('[DEBUG]user input is valid')
          if command_values[0] == 'disconnect':
            client_socket.close()
            return
          if command_values[0] == 'window':
            print ('window')
          if command_values[0] == 'get':
            if debug:
              print('[DEBUG]get file ' + command_values[1])
            request = 'FILERECEIVE:'+command_values[1]
            client_socket.send(request.encode())
            if debug:
              print('sent content: '+request)
            try:
              filename = 'get/'+command_values[1]
              count = 0
              
              while (os.path.exists(filename) == False):
                count = count + 1
                filename = filename + count

              f = open('get/'+command_values[1],'wb')

              if debug:
                print('[DEBUG]opened file at location ' +'get/'+command_values[1] )
              
              content = client_socket.recv(1024).decode()
              
              while content :
                if debug:
                  print('[DEBUG]received content: '+content)
              
                f.write(content.encode())
                content = client_socket.recv(1024).decode()
          
                if 'ENDPOST' in content:
                  f.close()
                  if debug:
                    print('[DEBUG]File closed')
                    print ('[DEBUG]Completed receiving {0} '.format(command_values[1]) )
                  content = None
            except IOError:
              print('could not open file')   
              
          if command_values[0] == 'post':
            if debug:
              print('[DEBUG]post/upload file ' + command_values[1])
            try:
              f = open(command_values[1],'rb')
              if debug:
                print('[DEBUG]File,{0} opened'.format(command_values[1]))
              request = 'FILESEND:'+command_values[1]
              client_socket.send(request.encode())
              if debug:
                print('[DEBUG]sent content: '+ request)
              content = f.read(1024)
              while (content):
                client_socket.send(content)
                content = f.read(1024)
                if debug:
                  print('[DEBUG]sent content: ' + content.decode())
              f.close()
              client_socket.send('ENDPOST'.encode())
              if debug:
                print('[DEBUG] Completed posting {0}'.format(command_values[1]))
            except FileNotFoundError:
              print('File does not exist')
              client_socket.close()
        else:
          print('please put in your command again')
  except:
    print('Something went wrong / user terminated the client')
    try:  
      client_socket.close()
      if debug:
        print('[DEBUG] Closing Socket')
    except UnboundLocalError:
      print('[DEBUG] Socket has not been initialized')

    try:
      f.close()
      if debug:
        print('[DEBUG] Closing File')
    except UnboundLocalError:
      print('[DEBUG] File has not been initialized')


if __name__ == '__main__':
  args = get_args()
  global server, port, debug
  server = args.server
  port = args.port
  debug = args.debug
  main()

#./sensor-udp -s 172.17.0.3 -p 8591 –u 'Room100SE' -c 'eye<3sockets!' -r 68.2
