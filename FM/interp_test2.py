import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
from scipy import signal
from scipy import interpolate
import pyaudio
import wave
import Queue
from ctypes import *
C_lib = CDLL("./C_lib.so")


#get the audio data
filepath="/home/sjh/Desktop/FM/1.wav"
wf = wave.open(filepath,'rb')
params = wf.getparams()
nchannels,samplewidth,framerate,nframes = params[:4]
data = wf.readframes(nframes)
raw_data = np.fromstring(data,dtype=np.short)

#set the buffer size
frame_duration = 20e-3
sample_rate = params[2]
file_sample_num = params[3]
frame_len = sample_rate * frame_duration
frame_num = int(np.floor(file_sample_num/frame_len))
frame_len = int(frame_len)


#modulation
cum_data = np.cumsum(raw_data) / float(framerate)
m=3.1
fc=3000
t = np.arange(0, nframes) * (1.0 / framerate)
mod_data = np.cos(m*cum_data+2*np.pi*t*fc)+1j*np.sin(m*cum_data+2*np.pi*t*fc)

#interpolation
ssf = 1.92e6
osr = int(ssf/sample_rate)
audio_len = file_sample_num/1000
tar_t = np.arange(0, audio_len)*(1.0 / ssf)
f = interpolate.interp1d(t[:audio_len],mod_data[:audio_len],'quadratic')
interp_data = f(tar_t)
