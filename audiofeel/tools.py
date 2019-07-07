#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 10:16:34 2018

@author: mikael
"""

import numpy as np
import scipy.signal as signal

def dct4(x):
    N = x.shape[0]
    n, k = np.meshgrid(range(N), range(N))
    cos_mat = np.cos(np.pi*(2*k+1)*(2*n+1)/(4*N))
    y = np.zeros(x.shape)
    if len(x.shape)>1:
        for k in range(x.shape[1]):
            y[:, k] = np.sum(x[:, k] * cos_mat, axis=1)
    else:
        y = np.sum(x * cos_mat, axis=1)
    return y*np.sqrt(2/N)

def idct4(x):
    return dct4(x)

def hop_split(x, length = 512, hop = 1):
    N = x.shape[0]
    # Calcul du nombre de segments en tenant compte du hop
    n_times = int(np.ceil((N-length)/hop))+1
    y = np.zeros((length, n_times))
    for k_time in range(n_times):
        x_segment = x[k_time*hop:min(k_time*hop+length, N)]
        M = x_segment.shape[0]
        y[0:M, k_time] = x_segment

    return y

def hop_win_split(x, win_type = 'hann', win_size = 512, hop = 1):
    # Calcul de la fenêtre
    win = signal.windows.get_window(win_type, win_size)
    # Découpage
    y = hop_split(x, win_size, hop)
    # Application fenêtre
    win_mat = np.tile(win, (y.shape[1], 1)).T
    y = y * win_mat

    return y

def hop_join(x, hop = 1):
    length = x.shape[0]
    n_times = x.shape[1]
    y = np.zeros(((n_times-1)*hop+length,))
    for k_time in range(n_times):
        x_segment = x[:, k_time]
        y[k_time*hop:k_time*hop+length] += x_segment

    return y

def hop_win_join(x, win_type = 'hann', hop = 1, cola = True):
    # Calcul de la fenêtre
    win = signal.windows.get_window(win_type, x.shape[0])
    # Application fenêtre
    win_mat = np.tile(win, (x.shape[1], 1)).T
    x_win = x * win_mat

    # Reconstruction
    y = hop_join(x_win, hop)
    if cola:
        w = hop_join(win_mat**2, hop)
    else:
        w = hop_join(win_mat, hop)

    # Condition pour reconstruction parfaite (COLA) détaillée ici https://gauss256.github.io/blog/cola.html
    y[np.where(w > 0)] /= w[np.where(w > 0)]
    return y

def overlap_split(x, win_size = 512, overlap = 0):
    hop - win_size - overlap
    return hop_split(x, win_size, hop)

def overlap_join(x, overlap = 0):
    win_size = x.shape[0]
    hop - win_size - overlap
    return hop_join(x, hop)

def overlap_win_split(x, win_type = 'hann', win_size = 512, overlap = 0):
    hop = win_size - overlap
    return hop_win_split(x, win_type, win_size, hop)

def overlap_win_join(x, win_type = 'hann', overlap = 0):
    win_size = x.shape[0]
    hop = win_size - overlap
    return hop_win_join(x, win_type, hop)




