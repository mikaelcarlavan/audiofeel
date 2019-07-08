#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 21:08:07 2019

@author: mikael
"""

import math as m
import ipywidgets as widgets
from ipywidgets import Layout
import numpy as np
import matplotlib.pyplot as plt
import pyaudio as pa

class Player:
     
    current_position = 0
    current_element = 0
    channels = 1
    samples = 1
    data = None
    bits_per_sample = 16
    sample_rate = 44100
    labels = None
    
    @property
    def element(self):
        return self.current_element
        
    @element.setter
    def element(self, current_element):
        self.current_element = current_element
        
    @property
    def progress(self):
        return self.current_position
        
    @progress.setter
    def progress(self, current_position):
        self.current_position = current_position
        total_time = int(self.samples/self.sample_rate)
        current_time = int(total_time*current_position/(self.channels*self.samples))
        time = total_time - current_time
        minutes = int(m.floor(time/60))
        seconds = time - 60*minutes
        
        self.progressSlider.value = self.progress
        self.timeLabel.value = "-%d:%02d" % (minutes, seconds)
        
    def __seek(self, change):
        self.progress = int(change['new'])
 
    def __switch(self, change):
        self.element = self.labels.index(change['new'])
        
    def __preprocess(self, data, bits_per_sample):
        buffer = np.array(data)

        if len(buffer.shape) == 1: # Vector
            buffer = np.reshape(buffer, (1, buffer.shape[0]))

        buffer = buffer.T            
        buffer = buffer.astype('float32')/(2**(bits_per_sample-1))
        return buffer
    
    def __callback(self, in_data, frame_count, time_info, status_flags):
        block_size = frame_count*self.channels
        out_data = self.data[self.element][self.progress:self.progress+block_size]
        self.progress += block_size
        
        flag = pa.paContinue
        return (out_data, flag)
    
    def __init__(self, data, labels = None, bits_per_sample = 16, sample_rate = 44100, frames_per_buffer = 1024):
        
        current_element = 0
        processed_data = []
        if type(data) is tuple:
            for buffer in data:     
                buffer = self.__preprocess(buffer, bits_per_sample)
                processed_data.append(buffer.flatten())
                self.channels = 1 if len(buffer.shape) == 1 else buffer.shape[1]
                self.samples = buffer.shape[0]
                
                current_element += 1
        else:
            buffer = self.__preprocess(data, bits_per_sample)
            processed_data.append(buffer.flatten())
            self.channels = 1 if len(buffer.shape) == 1 else buffer.shape[1]
            self.samples = buffer.shape[0] 

        self.data = np.array(processed_data)
        self.current_position = 0
        self.current_element = 0
        self.sample_rate = sample_rate
        self.bits_per_sample = bits_per_sample
        
        self.labels = [i+1 for i in range(self.data.shape[0])] if labels is None else labels

        # Init display
        self.playButton = widgets.Button(
            disabled = False,
            tooltip = 'Lecture',
            icon = 'play',
            layout = Layout(width = '40px', margin = '0px')
        )

        self.pauseButton = widgets.Button(
            disabled = False,
            tooltip = 'Pause',
            icon = 'pause',
            layout = Layout(width = '40px', margin = '0px')
        )

        self.stopButton = widgets.Button(
            disabled = False,
            tooltip = 'Stop',
            icon = 'stop',
            layout = Layout(width = '40px', margin = '0px')
        )

        self.progressSlider = widgets.IntSlider(
            value = 0,
            min = 0,
            max = self.samples * self.channels,
            step = frames_per_buffer,
            disabled = False,
            continuous_update = True,
            orientation = 'horizontal',
            readout = False,
            layout = Layout(margin='0px 10px')
        )

        self.channelsSelection = widgets.RadioButtons(
            options = self.labels,
            disabled = False,
            description = 'Sample'
        )
        
        total_time = int(self.samples/self.sample_rate)
        minutes = int(m.floor(total_time/60))
        seconds = total_time - 60*minutes
        
        self.timeLabel = widgets.Label(value="-%d:%02d" % (minutes, seconds))
        
        self.progressSlider.observe(self.__seek, names='value')
        self.channelsSelection.observe(self.__switch, names='value')
            
        self.playButton.on_click(self.start)
        self.stopButton.on_click(self.stop)
        self.pauseButton.on_click(self.pause)
            
        hbox = widgets.HBox([self.playButton, self.pauseButton, self.stopButton, self.progressSlider, self.timeLabel])
        vbox = widgets.VBox([self.channelsSelection, hbox])

        display(vbox)
        
        self.p = pa.PyAudio()
        self.stream = self.p.open(format=pa.paFloat32, channels=self.channels, frames_per_buffer=frames_per_buffer, rate=self.sample_rate, start=False, output=True, stream_callback=self.__callback)
        
    def start(self, b = None):
        self.stream.start_stream()
        
    def stop(self, b = None):
        self.progress = 0
        self.stream.stop_stream()
        
    def pause(self, b = None):
        self.stream.stop_stream()
        
    def close(self):
        self.stream.close()
        self.p.terminate()
        
        