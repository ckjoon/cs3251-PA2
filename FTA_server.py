#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, threading, time
from socket import *

command = ''

def input_thread():
    global command
    while True:
      command = input("> ")


def get_args():
  parser = argparse.ArgumentParser(description='Run ATCP Server.')
  parser.add_argument('-p', '--port', type=int, required=True, help='port of the server')
  parser.add_argument('-d', '--debug', action='store_true', help='debugging output')

  return parser.parse_args()


def main():
  #try:
  ip_addr = '172.17.0.2'
  server_port = port
  server_socket = socket(AF_INET, SOCK_STREAM)
  server_socket.bind((ip_addr, port))
  server_socket.listen(15)
  print('The server is running on {0} port {1}'.format(ip_addr, port))
  while True:
    conn_socket, addr = server_socket.accept()
    content = conn_socket.recv(1024).decode()
    send = False
    while (content):
      if send == False:
        if "FILESEND" in content:
          if debug:
            print('[DEBUG]File will be sent from client')
          filename = content.split(':')
          f = open('post/'+filename[1],'wb')
          content = conn_socket.recv(1024).decode()
        elif "FILERECEIVE" in content:
          if debug:
            print('File will be sent to the client')
          filename = content.split(':')
          f = open(filename[1],'rb')
          send = True  
        else:        
          print('inside receiving')
          f.write(content.encode())
          content = conn_socket.recv(1024).decode()
          print(content)
          if 'ENDPOST' in content:
            f.close()
            content = None

      if send:
        if debug:
          print('[DEBUG]inside sending')
        content = f.read(1024)
        if debug:
          print(content.decode())
        conn_socket.send(content)
        if 'ENDPOST' in content.decode():
          f.close()
          content = None
    if (send):
      conn_socket.send('ENDPOST'.encode())
    if(debug):
      print('Waiting for client\'s request.')

    #if command:
      # print(command)
      #print(command)
      #print('inside command')
  """      
  except:
    print('Something went very wrong...')
    server_socket.close()
  """  

if __name__ == '__main__':
  args = get_args()
  global port, debug
  port = args.port
  debug = args.debug
  #t = threading.Thread(target = input_thread)
  #t.start()
  main()

