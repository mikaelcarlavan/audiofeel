#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 10:06:46 2019

@author: mikael
"""
import struct
import math as m
import numpy as np

def to_float80(x):
    sign = 0
    exponent = 0
    
    if (x < 0):
        sign = 0x8000
        x = -x

    mantisse_h = 0
    mantisse_l = 0
    mantisse = 0
    
    if (x != 0):
        (mantisse, exponent) = m.frexp(x)
        if ((exponent > 16384) | (mantisse >= 1)):
            exponent = 0x7fff
            mantisse = 0
        else:
            exponent += 16382
            if (exponent < 0):
                mantisse = m.ldexp(mantisse, exponent)
                exponent = 0
            
    sign_exponent = sign | exponent
    mantisse = m.ldexp(mantisse, 32)         
    round_mantisse = m.floor(mantisse)
    mantisse_h = round_mantisse
    mantisse = m.ldexp(mantisse - round_mantisse, 32) 
    round_mantisse = m.floor(mantisse)
    mantisse_l = round_mantisse
    
    y = struct.pack('>HLL', sign_exponent, mantisse_h, mantisse_l)    
    
    return y
    
class AIFFWriter:

    @property
    def channels(self):
        return self._channels

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def bits_per_sample(self):
        return self._bits_per_sample

    @property
    def frames(self):
        return self._frames

    @property
    def data(self):
        return self._data

    def __init__(self, filename, data, bits_per_sample = 16, sample_rate = 44100.0):
        # data can be a list of channels, or a numpy array of shape (channels, number of samples)
        data = np.array(data)

        if len(data.shape) == 1: # Vector
            data = np.reshape(data, (1, data.shape[0]))

        data = data.T

        bits_per_sample = int(bits_per_sample)
        data_type = 2**(np.ceil(np.log2(bits_per_sample/8)) + 3)
        data_type = int(data_type)
        padding =  data_type - bits_per_sample 

        self._writer = open(filename, "wb")
        self._channels = 1 if len(data.shape) == 1 else data.shape[1]
        self._frames = data.shape[0]
        self._sample_rate = sample_rate
        self._bits_per_sample = bits_per_sample
        
        # Cast
        data = np.floor(data).astype('int%d' % data_type)
        self._data = data.flatten() * (2**padding)

        self._write()

    def _write(self):
        bits_per_sample = self.bits_per_sample
        samples = self.frames * self.channels
        data = self.data
        data_type = 2**(np.ceil(np.log2(bits_per_sample/8)) + 3)
        data_type = int(data_type)

        # FORM chunk is 12 bytes, COMM chunk is 26 bytes, SSND chunk is data size in bytes + 16
        ssnd_size = np.ceil(samples * data_type/8) + 16
        ssnd_size = int(ssnd_size)
        form_size = 12
        comm_size = 26
        file_size = form_size + comm_size + ssnd_size

        if data_type == 8:
            fmt = '>%db' 
        elif data_type == 16:
            fmt = '>%dh'
        elif data_type == 32:
            fmt = '>%di'
        else:
            fmt = '>%dq'

        with self._writer as file:
            # Write FORM chunk
            file.write('FORM'.encode('ascii'))
            file.write(struct.pack('>I', file_size - 8))
            file.write('AIFF'.encode('ascii'))
            
            # Write COMM chunk
            file.write('COMM'.encode('ascii'))
            file.write(struct.pack('>I', comm_size - 8))
            file.write(struct.pack('>H', self.channels))
            file.write(struct.pack('>I', self.frames))
            file.write(struct.pack('>H', self.bits_per_sample))
            file.write(to_float80(self.sample_rate))
            
            # Write SSND chunk
            file.write('SSND'.encode('ascii'))
            file.write(struct.pack('>I', ssnd_size - 8))
            file.write(struct.pack('>I', 0)) # Offset
            file.write(struct.pack('>I', 0)) # Block size
            file.write(struct.pack(fmt % samples, *data)) # Data
            file.close()