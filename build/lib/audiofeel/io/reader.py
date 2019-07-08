#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 18:42:13 2019

@author: mikael
"""
import numpy as np
from .aiff.reader import AIFFReader

def aiff_read(filename):
    reader = AIFFReader(filename)
    data = reader.getAllChannels()
    data = np.array(data).astype('double')
    return data