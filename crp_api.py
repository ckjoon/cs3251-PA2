#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from socket import *
import hashlib
import random
import math
import struct


class CRPSocket:
  def __init__(self, ip_addr='', port=None, server=False, window_size=65485):
    self.udp_socket = socket(AF_INET, SOCK_DGRAM)
    #self.src_ip = ip_addr
    self.src_port = port
    self.window_size = window_size
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
    packet = Packet(msg)
    print('is it valid: {}'.format(packet.is_valid()))
    print('packet type: {}'.format(packet.packet_type()))
    if packet.is_valid():
      if packet.packet_type() == 'SYN':
        print('Server is sending out SYNACK to client')
        send_SYNACK(client_addr, packet)
      elif packet.packet_type() == 'ACK':
        print('Server received ACK from client during handshake!')
        #the connection has established; flipping ack and seq number here because of client/server flipping nature of those
        if client_addr[0] not in self.open_connections.keys():
          new_connection  = Connection(packet.ack_num, packet.seq_num, self, client_addr[0], client_addr[1], window_size=packet.window_size)
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
    print(seq_num)
    self.send_packet(dst_ip=dst_ip, dst_port=dst_port, seq_num=seq_num, ack_num=ack_num, syn=True)
    print('Client sent out SYN to server, waiting for SYNACK!')
    #syn_header = Header(self.src_port, dst_port, syn=True, ack=False, fin=False, seq_num=self.seq_num, ack_num=self.ack_num)
    #syn_packet = syn_header.packet()
    #self.socket.sendto(syn_packet, (dst_ip, dst_port))

    #ready to receive SYNACK packet from the server
    msg, server_addr = self.udp_socket.recvfrom(2048)
    print('Packet received!')
    packet = Packet(msg)
    print('is it valid: {}'.format(packet.is_valid()))
    print('packet type: {}'.format(packet.packet_type()))
    if packet.is_valid() and packet.packet_type() == 'SYNACK':
      print('Client received SYNACK from server during handshake!')
      self.send_ACK(server_addr, packet)
      print('Connection to server at {0}:{1} establieshed successfully!'.format(server_addr[0], server_addr[1]))
      return Connection(packet.ack_num, packet.seq_num, self, server_addr[0], server_addr[1], window_size=packet.window_size)

    else:
      raise Exception('Something went wrong during 3-way handshake')

  def send_packet(self, dst_ip, dst_port, seq_num, ack_num, syn=False, ack=False, fin=False, window=None, data=None):
    header = Header(self.src_port, dst_port, syn=syn, ack=ack, fin=fin, seq_num=seq_num, ack_num=ack_num)
    packet = header.packet()
    self.udp_socket.sendto(packet, (dst_ip, dst_port))


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
  def __init__(self, seq_num, ack_num, custom_socket, dst_ip, dst_port, window_size=65485):
    self.seq_num = seq_num
    self.ack_num = ack_num
    self.window_size = window_size
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
        msg, addr = self.custom_socket.udp_socket.recvfrom(self.window_size)
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
    window_size = self.window_size / 4 #SWS; in terms of packets
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
      relative_last_frame_to_send = min(relative_start+window_size-1,num_chunks-1)
      attempt = 0
      try:
        for i in range(relative_start, last_frame_sent):
          self.custom_socket.send_packet(self.dst_ip, self.dst_port, seq_num=last_ack_received+i, ack_num=last_seq_received, data=chunk)

        msg, addr = self.custom_socket.udp_socket.recvfrom(size)
        last_packet_received = Packet(msg)
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
  def __init__(self, b):
    b = bytearray(b)
    print(b)
    self.raw = b
    self.src_port = bytes(b[:2])
    self.dst_port = bytes(b[2:4])
    self.seq_num = bytes(b[4:8])
    self.ack_num = bytes(b[8:12])

    print(int.from_bytes(bytearray(b[12]), byteorder='big') >> 7)
    self.ack = (b[12] >> 7) == 1
    self.syn = ((b[12] >> 6) & 0b01) == 1
    self.fin = ((b[12] >> 5) & 0b001) == 1
    self.window = bytes(b[20:24])
    self.checksum = bytes(b[24:30])
    self.data = 0
    if len(b) > 29:
      self.data = bytes(b[30:])

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
    elif self.fin and (self.ack or self.syn):
      print('PACKET TYPE ERROR ERRROR ERROR!!!')
    return action


  def is_valid(self):
    rest_of_packet = self.raw[:24]
    rest_of_packet.extend(bytearray(self.data))

    m = hashlib.md5()
    #print(rest_of_packet)
    m.update(bytes(rest_of_packet))
    calc_checksum = bytes(bytearray(m.digest())[-4:])

    return self.checksum == calc_checksum


class Header:

  def __init__(self, src_port, dst_port, syn=False, ack=False, fin=False, seq_num=None, ack_num=None, window_size=None, data=0):
    self.src_port = src_port
    self.dst_port = dst_port

    #if not seq_num:
    #  seq_num = uuid.uuid4()
    self.seq_num = seq_num
    #if not ack_num:
    #  ack_num = uuid.uuid4()
    self.ack_num = ack_num
    self.window_size = window_size
    if not window_size:
      self.window_size = 65485
    self.params = [ack, syn, fin]
    self.data = data

  def packet(self):
    b = bytearray()
    b.extend( bytearray( self.src_port.to_bytes(2, byteorder="big") ) )
    b.extend( bytearray( self.dst_port.to_bytes(2, byteorder="big") ) )
    b.extend( bytearray( self.seq_num.to_bytes(4, byteorder="big") ) )
    b.extend( bytearray( self.ack_num.to_bytes(4, byteorder="big") ) )
    parameter = self.form_param()
    b.extend( bytearray( parameter.to_bytes(2, byteorder="big") ) )
    b.extend( bytearray( self.window_size.to_bytes(2, byteorder="big") ) )

    checksum_b = b[:]
    checksum_b.extend( bytearray( self.data.to_bytes(4, byteorder="big") ) )

    md5 = self.form_checksum(checksum_b)

    b.extend( bytearray( md5 ) )
    if self.data:
      b.extend( bytearray( self.data.to_bytes(4, byteorder="big") ) )

    return bytes(b)

  def form_checksum(self, b):
    m = hashlib.md5()
    #print(bytes(b))
    m.update(bytes(b))
    #print(m.digest())
    return bytes(bytearray(m.digest())[-4:])

  def form_param(self):
    b = 0
    for i in range(3):
      b += self.params[i]*10^(2-i)

    return b

