#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from socket import *
import hashlib
import random
import math
import struct
import traceback


class CRPSocket:
  def __init__(self, ip_addr='', port=None, server=False, window=65485, debug=False):
    self.udp_socket = socket(AF_INET, SOCK_DGRAM)
    self.debug = debug

    self.src_port = port
    self.recv_window = window
    self.server = server
    if self.server:
      self.udp_socket.bind( (ip_addr, port) )

  def initiate_close(self):
    self.udp_socket.settimeout(3)
    attempts = 0
    while attempts < 3:
      try:
        self.send_FIN()
        msg, client_addr = self.udp_socket.recvfrom(65485)
        packet = Packet()
        packet.from_bytes(msg)
        if packet.is_valid and packet.type == 'ACK' and packet.ack_num == (self.seq_num + 1) and packet.seq_num == self.ack_num:
          if self.debug:
            print('ACK for closing received, waiting for FIN!')
          msg, client_addr = self.udp_socket.recvfrom(65485)
          packet = Packet()
          packet.from_bytes(msg)
          if packet.is_valid and packet.type == 'FIN' and packet.ack_num == (self.seq_num + 1) and packet.seq_num == self.ack_num+1:
            if self.debug:
              print('FIN for closing received, sending ACK and terminating!')
            self.udp_socket.close()
      except:
        attempts += 1
    print('Closing, but not gracefully')
    self.udp_socket.close()

  def accept(self):
    '''
    Contains step 2 in the 3-way handshake is called from here upon reception of a valid SYN packet. The server sends out a SYNACK packet to the client.
    '''

    while True:
      msg, client_addr = self.udp_socket.recvfrom(65485)
      if self.debug:
        print('Packet received!')
      packet = Packet()
      packet.from_bytes(msg)
      if self.debug:
        print(packet)
      if packet.is_valid:
        if packet.type == 'SYN':
          if self.debug:
            print('Server is sending out SYNACK to client')
          self.send_SYNACK(client_addr, packet)
        elif packet.type == 'ACK':
          if self.debug:
            print('Server received ACK from client during handshake!')


          new_connection  = Connection(packet.ack_num, packet.seq_num+1, self, client_addr[0], client_addr[1], send_window=packet.window)

          print('Connection established with {0}:{1}!'.format(client_addr[0], client_addr[1]))
          return new_connection


  def connect(self, dst_ip, dst_port):
    '''
    Steps 1 and 3 of the 3-way handshake are called from here by the client.
    '''
    seq_num = random.SystemRandom().randint(0, 2^31)
    #ack_num is irrelevant here because server will generate his own one
    ack_num = 0

    #forming and sending a SYN packet to the server

    self.send_packet(dst_ip=dst_ip, dst_port=dst_port, seq_num=seq_num, ack_num=ack_num, syn=True)
    if self.debug:
      print('Client sent out SYN to server, waiting for SYNACK!')

    #ready to receive SYNACK packet from the server
    msg, server_addr = self.udp_socket.recvfrom(65485)
    if self.debug:
      print('Packet received!')
    packet = Packet()
    packet.from_bytes(msg)
    if self.debug:
      print('is it valid: {}'.format(packet.is_valid))
      print('packet type: {}'.format(packet.type))
    if packet.is_valid and packet.type == 'SYNACK':
      if self.debug:
        print('Client received SYNACK from server during handshake!')
      self.send_ACK(server_addr, packet)
      if self.debug:
        print('Connection to server at {0}:{1} establieshed successfully!'.format(server_addr[0], server_addr[1]))

      return Connection(packet.ack_num+1, packet.seq_num+1, self, server_addr[0], server_addr[1], send_window=packet.window)

    else:
      print(traceback.print_exc())
      raise Exception('Something went wrong during 3-way handshake')

  def send_packet(self, dst_ip, dst_port, seq_num, ack_num, syn=False, ack=False, fin=False, lst=False, data=0):
    packet = Packet()
    packet.from_arguments(self.src_port, dst_port, syn=syn, ack=ack, fin=fin, lst=lst, seq_num=seq_num, ack_num=ack_num, window=self.recv_window, data=data)
    if self.debug:
      print('sending:')
      print(packet)
    self.udp_socket.sendto(packet.raw, (dst_ip, dst_port))


  def send_ACK(self, server_addr, packet):
    '''
    Function that directly sends the ACK packet of the 3-way handshake. Called by the client.
    '''
    #Making seq_num sent by the client to be incremented ack_num from the server
    new_ack_num = packet.seq_num + 1
    #Client ack is server's ack_num
    new_seq_num = packet.ack_num


    self.send_packet(server_addr[0], server_addr[1], ack=True, seq_num=new_seq_num, ack_num=new_ack_num)

  def send_FIN(self, server_addr):
    '''
    Function that directly sends the FIN packet. Called by the client.
    '''
    #Making seq_num sent by the client to be incremented ack_num from the server
    new_ack_num = self.ack_num + 1
    #Client ack is server's ack_num
    new_seq_num = self.seq_num + 1

    self.send_packet(server_addr[0], server_addr[1], ack=True, seq_num=new_seq_num, ack_num=new_ack_num)

  def send_SYNACK(self, client_addr, packet):
    '''
    Function that directly sends the SYNACK packet of the 3-way handshake. Called by the server.
    '''
    #Making ack_num sent by server to be incremented seq_num from the client
    new_ack_num = packet.seq_num + 1
    #Generating new server seq_num
    new_seq_num = random.SystemRandom().randint(0, 2^31)

    self.send_packet(client_addr[0], client_addr[1], syn=True, ack=True, seq_num=new_seq_num, ack_num=new_ack_num)


class Connection:
  '''
  Gets returned as a result of a successful handshake to both server and client.
  '''
  def __init__(self, seq_num, ack_num, custom_socket, dst_ip, dst_port, send_window=65485):
    self.debug = custom_socket.debug
    self.seq_num = seq_num
    self.ack_num = ack_num
    self.send_window = send_window
    self.custom_socket = custom_socket
    self.dst_ip = dst_ip
    self.dst_port = dst_port


  def recv(self):
    '''
    Called by server
    '''
    attempt_num = 0
    buffer = []

    while attempt_num < 3:
      new_ack_num, buffer_data, is_last = self.buffer_helper()
      self.custom_socket.udp_socket.settimeout(3)
      if new_ack_num <= self.ack_num:
        attempt_num += 1
      else:
        self.ack_num = new_ack_num
        self.seq_num += 1

        attempt_num = 0
        self.send_ack()
        buffer.extend(buffer_data)

        if is_last:
          break
    if len(buffer) == 0:
      raise Exception("Error, no data was received")

    buffer = list(set(buffer))
    buffer.sort(key=lambda x: x[0])
    if self.debug:
      print('buffer length: {}'.format(len(buffer)))
      print('buffer: {}'.format(buffer))

    data = bytearray()

    for x in buffer:
      data.extend(bytearray(x[1]))
    min_i = 3
    for i in range(3):
      #print(data[i])
      if data[i] != 0:
        min_i = i
        break
    data = data[min_i:]

    self.custom_socket.udp_socket.settimeout(None)
    self.custom_socket.seq_num = self.seq_num
    self.custom_socket.ack_num = self.ack_num
    return bytes(data)

  def buffer_helper(self):
    '''
    Called by server
    '''
    received_buffer = set()
    last = False
    try:
      while len(received_buffer) < self.custom_socket.recv_window:
        msg, addr = self.custom_socket.udp_socket.recvfrom(65485)
        self.custom_socket.udp_socket.settimeout(3)
        packet = Packet()
        packet.from_bytes(msg)
        if packet.is_valid:
          received_buffer.add( (packet.seq_num, packet.data, packet.type) )
          if self.debug:
            print('receiving:')
            print(packet)
    except:
      if self.debug:
        print('size of buffer: {}'.format(len(received_buffer)))
      received_buffer = list(received_buffer)
      if len(received_buffer) == 0:
        return 0, [], False
      elif len(received_buffer) == 1:
        min_ack = received_buffer[0][0]
        min_ack_i = 0
      elif len(received_buffer) > 1:
        received_buffer.sort(key=lambda x: x[0])
        for i in range(1, len(received_buffer)):
          if received_buffer[i-1][0] + 1 == received_buffer[i][0]:
            min_ack_i = i
            min_ack = received_buffer[i][0]
          else:
            break

      if received_buffer[min_ack_i][2] == 'LST':
        last = True

      return (min_ack+1, received_buffer[:min_ack_i+1], last)


  def send_data(self, data):
    '''
    Used by client to send data.
    data (bytes): data to be sent.
    '''

    data_chunks = []
    data = bytearray(data)
    if self.debug:
      print(data)
    r = len(data) % 4
    padding = (4 - r) % 4
    start = 4 - r

    first_chunk = bytearray()
    for i in range(padding):
      first_chunk.append(0x0)
    for i in range(4-padding):
      first_chunk.append(data[i])

    data_chunks.append(bytes(first_chunk))

    initial_seq_num = self.seq_num

    for i in range(start, len(data)-3, 4):
      data_chunks.append(bytes(data[i:i+4]))

    num_chunks = len(data_chunks)
    last_ack_received = initial_seq_num

    while last_ack_received < (initial_seq_num + num_chunks):
      window = self.send_window

      relative_start = last_ack_received - initial_seq_num
      relative_last_frame_to_send = min(relative_start+window-1,num_chunks-1)
      attempt = 0
      if self.debug:
        print('relative start: {}'.format(relative_start))
        print('relative_last_frame_to_send: {}'.format(relative_last_frame_to_send))
      try:
        for i in range(relative_start, relative_last_frame_to_send+1):
          chunk = data_chunks[i]

          lst = False
          if i == (num_chunks-1):
            lst = True

          self.custom_socket.send_packet(self.dst_ip, self.dst_port, seq_num=last_ack_received+i, ack_num=self.ack_num, lst=lst, data=chunk)
          self.ack_num += 1
        if self.debug:
          print('waiting for ack')
        msg, addr = self.custom_socket.udp_socket.recvfrom(65485)

        last_packet_received = Packet()
        last_packet_received.from_bytes(msg)

        self.send_window = last_packet_received.window
        if self.debug:
          print(last_packet_received)

        last_ack_received = last_packet_received.ack_num
        if self.debug:
          print('last_ack_received: {}'.format(last_ack_received))
          print('initial_seq_num: {}'.format(initial_seq_num))
          print('num_chunks: {}'.format(num_chunks))

        attempt = 0
      except:
        print(traceback.print_exc())
        if attempt < 3:
          print('Attempt {0} failed, resending the exact same window'.format(attempt))
          attempt += 1
        else:
          raise Exception("All attempts at sending failed, retry again")
    self.seq_num = last_ack_received
    self.ack_num = self.ack_num
    #print('Data sent successfully!')

  def send_ack(self):
    '''
    Server sends ACK to client to acknowledge receptance of data.
    '''

    self.custom_socket.send_packet(self.dst_ip, self.dst_port, ack=True, seq_num=self.seq_num, ack_num=self.ack_num)

class Packet:

  def from_bytes(self, b):
    b = bytearray(b)

    self.raw = b
    self.src_port = struct.unpack(">H", b[:2])[0]

    self.dst_port = struct.unpack(">H", b[2:4])[0]
    self.seq_num = struct.unpack(">I", b[4:8])[0]
    self.ack_num = struct.unpack(">I", b[8:12])[0]

    self.ack =  (b[12] >> 3) == 1
    self.syn =  ((b[12] >> 2) & 0b01) == 1
    self.fin = ((b[12] >> 1) & 0b001) == 1
    self.lst = (b[12] & 0b0001) == 1

    self.window = struct.unpack(">H", b[16:18])[0]
    self.checksum = bytes(b[18:20])
    self.data = bytes(b[20:])
    self.is_valid = self.is_valid()
    self.type = self.packet_type()

  def from_arguments(self, src_port, dst_port, syn=False, ack=False, fin=False, lst=False, seq_num=None, ack_num=None, window=None, data=0):
    self.src_port = src_port
    self.dst_port = dst_port

    self.seq_num = seq_num

    self.ack_num = ack_num
    self.window = window
    if not window:
      self.window = 65485
    self.ack =  ack
    self.syn =  syn
    self.fin = fin
    self.lst = lst
    self.data = data
    self.raw = self.pack()
    self.type = self.packet_type()
    self.is_valid = self.is_valid()

  def pack(self):
    b = bytearray()
    b.extend( bytearray( self.src_port.to_bytes(2, byteorder="big") ) )
    b.extend( bytearray( self.dst_port.to_bytes(2, byteorder="big") ) )
    b.extend( bytearray( self.seq_num.to_bytes(4, byteorder="big") ) )
    b.extend( bytearray( self.ack_num.to_bytes(4, byteorder="big") ) )
    parameter = self.form_param()


    b.extend( bytearray( parameter.to_bytes(1, byteorder="big") ) )
    padding = 0
    b.extend( bytearray( padding.to_bytes(3, byteorder="big" ) ) )
    b.extend( bytearray( self.window.to_bytes(2, byteorder="big") ) )

    checksum_b = b[:]
    if type(self.data) != bytes:
      checksum_b.extend( bytearray( self.data.to_bytes(4, byteorder="big") ) )
    else:
      checksum_b.extend(bytearray(self.data))
    md5 = self.form_checksum(checksum_b)
    self.checksum = md5

    b.extend( md5 )
    if type(self.data) != bytes:
      b.extend( bytearray( self.data.to_bytes(4, byteorder="big") ) )
    else:
      b.extend(bytearray(self.data))

    return bytes(b)

  def packet_type(self):
    action = 'DATA'
    if self.ack and self.syn:
      action = 'SYNACK'
    elif self.ack:
      action = 'ACK'
    elif self.syn:
      action = 'SYN'
    elif self.fin:
      action = 'FIN'
    elif self.lst:
      action = 'LST'
    elif self.fin and (self.ack or self.syn):
      print('PACKET TYPE ERROR ERRROR ERROR!!!')
    return action


  def is_valid(self):

    rest_of_packet = bytearray(self.raw[:13])
    padding = 0
    rest_of_packet.extend( bytearray( padding.to_bytes(3, byteorder="big" ) ) )

    rest_of_packet.extend(bytearray(self.raw[16:18]))
    rest_of_packet.extend(bytearray(self.raw[20:]))

    calc_checksum = self.form_checksum(rest_of_packet)

    return self.checksum == calc_checksum

  def form_checksum(self, b):
    m = hashlib.md5()
    m.update(b)
    return m.digest()[-2:]

  def form_param(self):
    b = 0
    params = [self.ack, self.syn, self.fin, self.lst]
    for i in range(4):
      bit = 1 if params[i] else 0
      b  = (b << 1) + bit
    return b

  def __str__(self):
     return '\nbyte_rep: {0}\nsrc_port: {1}\ndst_port: {2}\nseq_num: {3}\nack_num: {4}\nack: {5}\nsyn: {6}\nfin: {7}\nlst: {8}\nwindow: {9}\nchecksum: {10}\ndata: {11}\nvalid: {12}\ntype: {13}\n\n'.format(bytes(self.raw), self.src_port, self.dst_port, self.seq_num, self.ack_num, self.ack, self.syn, self.fin, self.lst, self.window, self.checksum, self.data, self.is_valid, self.type)

