#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 09:57:50 2019

@author: mikael
"""
import struct
import math as m
import numpy as np

def from_float80(x):
    sign_exponent, mantisse_h, mantisse_l = struct.unpack('>HLL', x)
    sign = sign_exponent & 0xa000
    sign = sign >> 15
    exponent = sign_exponent & 0x7fff
    if (exponent == 0 & mantisse_h == 0 & mantisse_l == 0):
        y = 0
    else:
        if (exponent == 0x7fff):
            y = np.nan
        else:
            exponent -= 16383
            exponent -= 31
            y = m.ldexp(mantisse_h, exponent)
            exponent -= 32
            y += m.ldexp(mantisse_l, exponent)

    return y if sign == 0 else -y
    
class AIFFReader:

    @property
    def channels(self):
        return self._channels

    @property
    def smaple_rate(self):
        return self._sample_rate

    def __init__(self, filename):
        self._reader = open(filename, "rb")
        self._read()

    def _read(self):
        with self._reader as file:
            # Read FORM chunk
            chunk_name = file.read(4).decode('ascii')
            file_size = struct.unpack('>I', file.read(4))[0]
            format = file.read(4).decode('ascii') # AIFF
            remaining_size = file_size - 4
            
            # Read COMM chunk
            chunk_name = file.read(4).decode('ascii')
            remaining_size -= 4
            chunk_size = struct.unpack('>I', file.read(4))[0]
            remaining_size -= 4
            channels = struct.unpack('>H', file.read(2))[0]
            remaining_size -= 2
            frames = struct.unpack('>I', file.read(4))[0]
            remaining_size -= 4
            bits_per_sample = struct.unpack('>H', file.read(2))[0]
            remaining_size -= 2  
            sample_rate = from_float80(file.read(10))
            remaining_size -= 10
            
            # Read SSND chunk
            chunk_name = file.read(4).decode('ascii')
            remaining_size -= 4
            chunk_size = struct.unpack('>I', file.read(4))[0]
            remaining_size -= 4
            offset = struct.unpack('>I', file.read(4))[0]
            remaining_size -= 4
            block_size = struct.unpack('>I', file.read(4))[0]
            remaining_size -= 4
            comment = None
            if offset > 0:
                comment = file.read(offset).decode('ascii')
                
            sample_data_buffer = file.read(chunk_size - offset - 8)
            bytes_per_sample = bits_per_sample // 8
            padding = 0
            if bits_per_sample % 8:
                bytes_per_sample += 1
                padding = bytes_per_sample * 8 - bits_per_sample

            data_size = len(sample_data_buffer) // bytes_per_sample 
            if len(sample_data_buffer) % bytes_per_sample:
                data_size += 1
                
            if bits_per_sample <= 8:
                fmt = '>%db' 
            elif bits_per_sample > 8 & bits_per_sample <= 16:
                fmt = '>%dh'
            elif bits_per_sample > 16 & bits_per_sample <= 32:
                fmt = '>%di'
            else:
                fmt = '>%dq'
                
            data_buffer = struct.unpack(fmt % data_size, sample_data_buffer)
                
            self._channels = channels
            self._sample_rate = sample_rate
            self._data = []
            
            for ch in range(channels):
                self._data.append([i * (2**padding) for i in data_buffer[ch::channels]])

    def getChannel(self, channel):
        data = self.getAllChannels()
        return data[channel] if channel < self.channels else None

    def getAllChannels(self):
        return self._data

    def getLeftChannel(self):
        return self.getChannel(0)

    def getRightChannel(self):
        return self.getChannel(1)