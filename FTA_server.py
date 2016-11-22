#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, threading, time, os.path, traceback
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
  try:
    global window
    ip_addr = '172.17.0.2'
    server_port = port
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((ip_addr, port))
    server_socket.listen(15)
    print('The server is running on {0} port {1}'.format(ip_addr, port))
    while True:
      conn_socket, addr = server_socket.accept()
      closed = False
      while not closed: 
        content = conn_socket.recv(window).decode()
        send = False
        while (content):
          if send == False:
            if "FILESEND" in content:
              print('File will be sent from client')
              split_command = content.split(':')
              filename = 'post/' + split_command[1]
              count = 0
              while (os.path.exists(filename)):
                print('[Debug] duplicate detected')
                count = count + 1
                extension = split_command[1].split('.')
                filename= ('{0} ({1}).{2}').format('post/'+extension[0], str(count), extension[1])
                print('[Debug] File name  ' +filename)
              f = open(filename,'wb')
              print('Created file {0} to receive from client'.format(filename))
              content = conn_socket.recv(window).decode()
              if debug:
                print('[DEBUG] Received Content: ' + str(content.encode()))
            elif "FILERECEIVE" in content:
              print('File will be sent to the client')
              filename = content.split(':')
              try:
                f = open(filename[1],'rb')
                print('Opened file {0}'.format(filename))
              except IOError:
                print('File does not exist')
                client_socket.close()
              send = True  
            else:   
              #Receive file from client     
              f.write(content.encode())
              content = conn_socket.recv(window).decode()
              if debug:
                  print('[DEBUG] Received Content: '+ str(content.encode()))

              print(content)
              if 'ENDPOST' in content:
                f.close()
                print('Completed receiving {0}'.format(filename))
                content = None
          if send:
            #send file to client     
            content = f.read(window)
            if debug:
              print('[DEBUG] sent content: '+ str(content.decode()))

            if debug:
              print(content.decode())
            conn_socket.send(content)
            if 'ENDPOST' in content.decode():
              f.close()
              print('Completed sending {0}'.format(filename[1]))
              content = None
        if (send):
          conn_socket.send('ENDPOST'.encode())
        if(debug):
          print('Waiting for client\'s request.')
    #if command:
      # print(command)
      #print(command)
      #print('inside command')

  except:
    print(traceback.print_exc())
    print('Something went very wrong...')
    try:  
      server_socket.close()
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
  global port, debug, window
  port = args.port
  debug = args.debug
  window = 1024
  main()

