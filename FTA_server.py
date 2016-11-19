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
    l = conn_socket.recv(1024).decode('utf-8')
    while (l):
      if("FileName" in l):
        print('filename')
        filename = l.split(':')
        f = open('output/'+filename[1],'wb')
      elif 'ENDPOST' in l:
        f.close()
      else:
        f.write(l.encode('utf-8'))
        print(l)
      l = conn_socket.recv(1024).decode('utf-8')
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
  global port
  port = args.port
  #t = threading.Thread(target = input_thread)
  #t.start()
  main()

