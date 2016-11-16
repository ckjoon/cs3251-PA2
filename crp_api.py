#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from socket import *
import hashlib
import ctypes
import uuid



class Connection:
  def __init__(self, src_ip, src_port, dst_ip, dst_port):
    self.src_ip = src_ip
    self.src_port = src_port
    self.dst_ip = dst_ip
    self.dst_port = dst_port



class Socket:
  def __init__(self, ip_addr, port):
    self.socket = socket(AF_INET, SOCK_DGRAM)
    self.src_ip = ip_addr
    self.src_port = port
    self.socket.bind( (ip_addr, port) )

  def listen(self):
    print('The server is running on {0} port {1}'.format(ip_addr, port))
    while True:
      msg, client_addr = server_socket.recvfrom(2048)
      packet = Packet(msg)
      if packet.validate():
        send_synack(client_addr)

  def connect(self, dst_ip, dst_port):
    self.dst_ip = dest_ip
    self.dst_port = dest_port
    self.seq_num = uuid.uuid4()
    self.ack_num = uuid.uuid4()

    syn_header = Header(self.src_port, self.dst_port, syn=True, ack=False, fin=False, seq_num=self.seq_num, ack_num=self.ack_num)
    syn_packet = syn_header.packet()
    self.socket.sendto(syn_packet, (dst_ip, dst_port) )



  def send_synack(self, dst_ip, dst_port):



class Packet:

  def __init__(self, b):
    b = bytearray(b)
    self.raw = b
    self.src_port = bytes(b[:2])
    self.dst_port = bytes(b[2:4])
    self.seq_num = bytes(b[4:8])
    self.ack_num = bytes(b[8:12])

    self.ack = (b[12] >> 7) == 1
    self.syn = ((b[12] >> 6) & 0b01) == 1
    self.fin = ((b[12] >> 5) & 0b001) == 1
    self.window = bytes(b[20:24])
    self.checksum = bytes(b[24:30])
    self.data = 0
    if len(b) > 29:
      self.data = bytes(b[30:])

  def validate(self):
    rest_of_packet = self.raw[:24].extend(bytearray(self.data))

    m = hashlib.md5()
    m.update(rest_of_packet.decode('utf-8'))
    calc_checksum = bytes(m.digest() & 0xffff)

    return self.checksum == calc_checksum


class Header:
  max_window_size = 65485
  int16 = ctypes.c_uint16
  int32 = ctypes.c_uint32
  fieldTypes = {
    'src_port': int16,
    'dst_port': int16,
    'seq_num': int32,
    'ack_num': int32,
    'parameter': int32,
    'window': int16,
    'checksum': int16
    }

  def __init__(self, src_port, dst_port, syn=False, ack=False, fin=False, seq_num=None, ack_num=None, window=max_window_size, data=None):
    self.src_port = src_port
    self.dst_port = dst_port

    #if not seq_num:
    #  seq_num = uuid.uuid4()
    self.seq_num = seq_num
    #if not ack_num:
    #  ack_num = uuid.uuid4()
    self.ack_num = ack_num

    self.window = window
    self.params = [fin, syn, ack]

  def packet(self):
    b = bytearray()
    b.extend( bytearray( field_types['src_port'](self.src_port) ) )
    b.extend( bytearray( field_types['dst_port'](self.dst_port) ) )
    b.extend( bytearray( field_types['seq_num'](self.seq_num) ) )
    b.extend( bytearray( field_types['ack_num'](self.ack_num) ) )
    parameter = self.form_param()
    b.extend( bytearray( field_types['parameter'](parameter) ) )
    b.extend( bytearray( field_types['window'](self.window) ) )
    md5 = self.form_checksum(b)
    b.extend( bytearray( field_types['checksum'](md5) ) )
    return bytes(b)

  def form_checksum(self, b):
    m = hashlib.md5()
    m.update(b.decode('utf-8'))
    return m.digest() & 0xffff

  def form_param(self):
    byte_params = []

    for i in range(3):
      if self.params[i]:
        b = 0b1 << i
        byte_params.append(b)

    if len(byte_params) > 1:
      params = reduce(lambda x,y: x | y, byte_params)
    elif len(byte_params) == 1:
      params = byte_params[0] << (32-3)
    else:
      params = 0

    return params


def socket(ip_addr, port):
  return Socket(ip_addr, port)
