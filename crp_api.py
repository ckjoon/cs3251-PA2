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
  def __init__(self, ip_addr='', port=None, server=False, window=65485):
    self.udp_socket = socket(AF_INET, SOCK_DGRAM)
    #self.src_ip = ip_addr
    self.src_port = port
    self.window = window
    if server:
      self.udp_socket.bind( (ip_addr, port) )
    self.open_connections = {}#key: client_ip_addr, val: connection object


  def accept(self):
    '''
    Contains step 2 in the 3-way handshake is called from here upon reception of a valid SYN packet. The server sends out a SYNACK packet to the client.
    '''
    #print('The server is running on {0} port {1}'.format(ip_addr, port))
    #while True:
    #print('server called .accept()')
    msg, client_addr = self.udp_socket.recvfrom(2048)
    print('Packet received!')
    packet = Packet()
    packet.from_bytes(msg)
    print(packet)
    if packet.is_valid:
      if packet.type == 'SYN':
        print('Server is sending out SYNACK to client')
        self.send_SYNACK(client_addr, packet)
      elif packet.type == 'ACK':
        print('Server received ACK from client during handshake!')
        #the connection has established; flipping ack and seq number here because of client/server flipping nature of those
        if client_addr[0] not in self.open_connections.keys():
          new_connection  = Connection(packet.ack_num, packet.seq_num, self, client_addr[0], client_addr[1], window=packet.window)
          self.open_connections[client_addr[0]] = new_connection
        return self.open_connections[client_addr[0]]

  def connect(self, dst_ip, dst_port):
    '''
    Steps 1 and 3 of the 3-way handshake are called from here by the client.
    '''
    seq_num = random.SystemRandom().randint(0, 2^31)
    #ack_num is irrelevant here because server will generate his own one
    ack_num = 0

    #forming and sending a SYN packet to the server
    #print(seq_num)
    self.send_packet(dst_ip=dst_ip, dst_port=dst_port, seq_num=seq_num, ack_num=ack_num, syn=True)
    print('Client sent out SYN to server, waiting for SYNACK!')
    #syn_header = Header(self.src_port, dst_port, syn=True, ack=False, fin=False, seq_num=self.seq_num, ack_num=self.ack_num)
    #syn_packet = syn_header.packet()
    #self.socket.sendto(syn_packet, (dst_ip, dst_port))

    #ready to receive SYNACK packet from the server
    msg, server_addr = self.udp_socket.recvfrom(2048)
    print('Packet received!')
    packet = Packet()
    packet.from_bytes(msg)
    print('is it valid: {}'.format(packet.is_valid))
    print('packet type: {}'.format(packet.type))
    if packet.is_valid and packet.type == 'SYNACK':
      print('Client received SYNACK from server during handshake!')
      self.send_ACK(server_addr, packet)
      print('Connection to server at {0}:{1} establieshed successfully!'.format(server_addr[0], server_addr[1]))
      print(packet)
      return Connection(packet.ack_num, packet.seq_num, self, server_addr[0], server_addr[1], window=packet.window)

    else:
      print(traceback.print_exc())
      raise Exception('Something went wrong during 3-way handshake')

  def send_packet(self, dst_ip, dst_port, seq_num, ack_num, syn=False, ack=False, fin=False, window=None, data=None):
    packet = Packet()
    packet.from_arguments(self.src_port, dst_port, syn=syn, ack=ack, fin=fin, seq_num=seq_num, ack_num=ack_num)
    self.udp_socket.sendto(packet.raw, (dst_ip, dst_port))


  def send_ACK(self, server_addr, packet):
    '''
    Function that directly sends the ACK packet of the 3-way handshake. Called by the client.
    '''
    #Making seq_num sent by the client to be incremented ack_num from the server
    new_ack_num = packet.seq_num + 1
    #Client ack is server's ack_num
    new_seq_num = packet.ack_num

    #forming the header
    #synack_header = Header(packet.dst_port, packet.src_port, syn=True, ack=True, fin=False, seq_num=new_seq_num, ack_num=new_ack_num)
    #packing it into a bytes object
    #synack_packet = synack_header.packet()
    #sending to the client over UDP
    #self.socket.sendto(synack_packet, client_addr)

    self.send_packet(server_addr[0], server_addr[1], ack=True, seq_num=new_seq_num, ack_num=new_ack_num)

  def send_SYNACK(self, client_addr, packet):
    '''
    Function that directly sends the SYNACK packet of the 3-way handshake. Called by the server.
    '''
    #Making ack_num sent by server to be incremented seq_num from the client
    new_ack_num = packet.seq_num + 1
    #Generating new server seq_num
    new_seq_num = random.SystemRandom().randint(0, 2^31)

    #forming the header
    #synack_header = Header(packet.dst_port, packet.src_port, syn=True, ack=True, fin=False, seq_num=new_seq_num, ack_num=new_ack_num)
    #packing it into a bytes object
    #synack_packet = synack_header.packet()
    #sending to the client over UDP
    #self.socket.sendto(synack_packet, client_addr)
    self.send_packet(client_addr[0], client_addr[1], syn=True, ack=True, seq_num=new_seq_num, ack_num=new_ack_num)


class Connection:
  '''
  Gets returned as a result of a successful handshake to both server and client.
  '''
  def __init__(self, seq_num, ack_num, custom_socket, dst_ip, dst_port, window=65485):
    self.seq_num = seq_num
    self.ack_num = ack_num
    self.window = window
    self.custom_socket = socket
    self.dst_ip = dst_ip
    self.dst_port = dst_port

  #def close(self):


  def recv(self):
    '''
    Called by server
    '''
    attempt_num = 0
    buffer = []
    while attempt_num < 3:
      new_ack_num, buffer_data  = self.buffer_helper()
      if new_ack_num <= self.ack_num:
        attempt_num += 1
      else:
        self.ack_num = new_ack_num
        self.seq_num += 1

        attempt_num = 0
        self.send_ack()
        buffer = buffer.extend(buffer_data)
        self.send_ack()
    if len(buffer) == 0:
      raise Exception("Error, no data was received")

    buffer = list(set(buffer))
    buffer.sort(key=lambda x,y: x[0] < y[0])
    data = bytes(bytearray([x[1] for x in buffer]))
    return data

  def buffer_helper(self):
    '''
    Called by server
    '''
    received_buffer = []
    try:
      while True:
        msg, addr = self.custom_socket.udp_socket.recvfrom(self.window)
        packet = Packet(msg)
        received_buffer.append( (packet.seq_num, packet.data) )
    except:
      received_buffer.sort(key=lambda x,y: x[0] < y[0])#doublecheck the equality sign direction
      if len(received_buffer) == 0:
        return 0, []
      elif len(received_buffer) == 1:
        min_ack = received_buffer[0][0]
      elif len(received_buffer) > 1:
        min_ack_i = 0
        for i in range(1, len(received_buffer)):
          if received_buffer[i-1][0] - received_buffer[i][0] > 1:
            min_ack = received_buffer[i-1][0]
            min_ack_i = i-1
      return min_ack+1, received_buffer[:min_ack_i]

  def send_data(self, data):
    '''
    Used by client to send data.
    data (bytes): data to be sent.
    recvd_packet (Packet): last received packet.
    '''
    window = self.window / 4 #SWS; in terms of packets
    #list of chunks of data in bytes that can fit in one packet
    data_chunks = []
    data = bytearray(data)
    start = len(data) % 4
    padding = 4 - start

    first_chunk = bytearray()
    for i in range(padding):
      first_chunk.append(0x0)
    for i in range(start):
      first_chunk.append(data[i])

    data_chunks.append(bytes(first_chunk))

    initial_seq_num = recvd_packet.ack_num #LAR


    for i in range(start, len(data), 4):
      data_chunks.append(bytes(data[i:i+4]))
    num_chunks = len(data_chunks)

    last_ack_received = initial_seq_num
    last_seq_received = recvd_packet.seq_num

    while last_ack_received < (initial_seq_num + num_chunks):

      relative_start = last_ack_received - initial_seq_num
      relative_last_frame_to_send = min(relative_start+window-1,num_chunks-1)
      attempt = 0
      try:
        for i in range(relative_start, last_frame_sent):
          self.custom_socket.send_packet(self.dst_ip, self.dst_port, seq_num=last_ack_received+i, ack_num=last_seq_received, data=chunk)

        msg, addr = self.custom_socket.udp_socket.recvfrom(size)
        last_packet_received = Packet()
        last_packet_received.from_bytes(msg)
        last_ack_received = last_packet_received.ack_num
        attempt = 0
      except:
        if attempt < 3:
          print('Attempt {0} failed, resending the exact same window'.format(attempt))
          attempt += 1
        else:
          raise Exception("All attempts at sending failed, retry again")


  def send_ack(self):
    '''
    Server sends ACK to client to acknowledge receptance of data.
    '''

    self.custom_socket.send_packet(self.dst_ip, self.dst_port, ack=True, seq_num=self.seq_num, ack_num=self.ack_num)

class Packet:

  #def __init__(self)
  def from_bytes(self, b):
    b = bytearray(b)
    print(b)
    #print(len(b))
    self.raw = b
    self.src_port = struct.unpack(">H", b[:2])[0]
    #print(self.src_port)
    self.dst_port = struct.unpack(">H", b[2:4])[0]
    self.seq_num = struct.unpack(">I", b[4:8])[0]
    self.ack_num = struct.unpack(">I", b[8:12])[0]

    self.ack =  (b[12] >> 3) == 1
    self.syn =  ((b[12] >> 2) & 0b01) == 1
    self.fin = ((b[12] >> 1) & 0b001) == 1
    self.lst = (b[12] & 0b0001) == 1

    self.window = struct.unpack(">H", b[16:18])[0]
    self.checksum = bytes(b[18:20])
    self.data = bytes(b[30:])
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

  def pack(self):
    b = bytearray()
    b.extend( bytearray( self.src_port.to_bytes(2, byteorder="big") ) )
    b.extend( bytearray( self.dst_port.to_bytes(2, byteorder="big") ) )
    b.extend( bytearray( self.seq_num.to_bytes(4, byteorder="big") ) )
    b.extend( bytearray( self.ack_num.to_bytes(4, byteorder="big") ) )
    parameter = self.form_param()
    #print(self.params)
    #print(parameter)
    #testing = parameter.to_bytes(1, byteorder="big")
    #print(int.from_bytes(testing, byteorder="big"))

    b.extend( bytearray( parameter.to_bytes(1, byteorder="big") ) )
    padding = 0
    b.extend( bytearray( padding.to_bytes(3, byteorder="big" ) ) )
    b.extend( bytearray( self.window.to_bytes(2, byteorder="big") ) )

    checksum_b = b[:]
    checksum_b.extend( bytearray( self.data.to_bytes(4, byteorder="big") ) )

    md5 = self.form_checksum(checksum_b)
    self.checksum = md5
    #print('checksum: {0}'.format(md5))
    b.extend( md5 )
    b.extend( bytearray( self.data.to_bytes(4, byteorder="big") ) )
    #print(b)
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
    #print('raw: {0}'.format(self.raw))
    rest_of_packet = bytearray(self.raw[:13])
    padding = 0
    rest_of_packet.extend( bytearray( padding.to_bytes(3, byteorder="big" ) ) )
    #print('rest_of_packet 1st slice: {0}'.format(rest_of_packet))
    rest_of_packet.extend(bytearray(self.raw[16:18]))
    rest_of_packet.extend(bytearray(self.raw[20:]))
    #print('array plugged into md5: {0}'.format(rest_of_packet))
    calc_checksum = self.form_checksum(rest_of_packet)
    #print('original checksum: {0}'.format(self.checksum))
    #print('calculated checksum: {0}'.format(calc_checksum))
    return self.checksum == calc_checksum

  def form_checksum(self, b):
    #print('array plugged into md5: {0}'.format(b))
    m = hashlib.md5()
    #print(bytes(b))
    m.update(b)
    #print(m.digest())
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

