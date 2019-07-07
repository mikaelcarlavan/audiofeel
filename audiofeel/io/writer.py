#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 18:49:13 2019

@author: mikael
"""
import numpy as np
from .aiff.writer import AIFFWriter

def aiff_write(filename, data, bits_per_sample = 16, sample_rate = 44100.0):
    writer = AIFFWriter(filename, data, bits_per_sample, sample_rate)
