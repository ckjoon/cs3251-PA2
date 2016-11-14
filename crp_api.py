#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from socket import *
import hashlib
import ctypes

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

  def connect(self, dst_ip, dst_port):
    self.dst_ip = dest_ip
    self.dst_port = dest_port
    self.seq_num = 0
    self.ack_num = 0
    #WORK IN PROGRESS


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

  def __init__(self, src_port, dst_port, syn=False, ack=False, fin=False, seq_num=0, ack_num=0, window=max_window_size):
    self.src_port = src_port
    self.dst_port = dst_port
    self.seq_num = seq_num
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

  def form_checksum(self):
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
      params = byte_params[0]
    else:
      params = 0

    return params


def socket(ip_addr, port):
  return Socket(ip_addr, port)
